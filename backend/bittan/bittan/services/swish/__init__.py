import requests
import json

from ...models.swish_payment_request import SwishPaymentRequestModel, PaymentErrorCode as SwishApiErrorCode, PaymentStatus as SwishApiStatus
from .swish_payment_request import SwishPaymentRequest, PaymentErrorCode, PaymentStatus
from enum import Enum
from uuid import uuid4
from datetime import datetime


instance = None

class SwishPaymentRequest:
	"""A class that represents all the user of this api needs to know about a payment"""
	
	def __init__(self, paymentRequest: SwishPaymentRequestModel):
		self.id = paymentRequest.id
		self.status = paymentRequest.status
		self.errorCode = paymentRequest.error_code
		self.token = paymentRequest.token
		
	def is_payed(self):
		return self.status == PaymentStatus.PAID
	
	id: str

	status: PaymentStatus 
	errorCode: PaymentErrorCode | None

	# Used to start the swish app. Used by the frontent to make the payment
	token: str | None

class SwishPaymentRequestResponse():
    """ This is the response that the official swish api sends after we have sent a request """
	status: SwishApiStatus
	error_code: SwishApiErrorCode 
	id: str 

	def __init__(self, response):
		self.id = response['id']
		self.status = SwishApiStatus.from_swish_api_status(response['status'])
		self.error_code = SwishApiErrorCode.from_swish_reponse_code(response['errorCode'])

class Swish():
	def __init__(self, swish_url, payee_alias, callback_url, cert_file_paths, callback_function):
		self.swish_url = swish_url
		self.payee_alias = payee_alias
		self.callback_url = callback_url
		self.payeee_reference_id = ""
		self.cert_file_paths = cert_file_paths

		self.callback_function = callback_function

		global instance
		instance = self

	def update_swish_payment_request(self, payment_request_response: dict, model: SwishPaymentRequestModel | None = None):
		payment_request_response = SwishPaymentRequestResponse(payment_request_response)
		if model is None:
			model = SwishPaymentRequestModel.objects.get(pk=payment_request_response.id)
		
		print(payment_request_response.status, type(payment_request_response.status))
		print(payment_request_response.error_code)
		model.error_code = payment_request_response.error_code
		model.status = payment_request_response.status

		model.swish_api_response = json.dumps(payment_request_response)

		model.save()
		return model


	def synchronize_payment_request(self, payment_request: SwishPaymentRequestModel | str):
		payment_request_id = None
		if isinstance(payment_request, str):
			payment_request_id = payment_request 
			payment_request = None
		else:
			payment_request_id = payment_request.id

		response = self.send_to_swish('GET', f'api/v1/paymentrequests/{payment_request_id}')
		# response = self.send_to_swish('GET', f'api/v1/paymentrequests/{payment_request_id}')
		# TODO Handle errors more elegantly
		response.raise_for_status()
		
		response_body = response.json()
		self.update_swish_payment_request(response_body, payment_request)

	def get_payment_request(self, id: str) -> SwishPaymentRequest:
		payment_request = SwishPaymentRequestModel.objects.get(pk=id)

		print(payment_request.status)

		if payment_request.status != SwishApiStatus.WAITING:
			return payment_request

		self.synchronize_payment_request(payment_request)
		return SwishPaymentRequest(payment_request)


	@staticmethod
	def generate_swish_id() -> str: 
		return str(uuid4()).replace('-', '').upper()
	
	def handle_swish_callback(self, response):
		payment_request_model = self.update_swish_payment_request(response)

		payment_request = SwishPaymentRequest(payment_request_model)
		self.callback_function(payment_request)


	def send_to_swish(self, method, path: str, data = None, **kwargs):
		return requests.request(method, f'{self.swish_url}{path}', cert=self.cert_file_paths, **kwargs)


	def create_swish_payment(self, amount: int, message="") -> SwishPaymentRequest:
			"""
			Tells Swish that we want to create a payment. Note: This function will call the callback efen if it directly returns a
			SwishPaymentRequest which has a status of Cancelled.

			@param amount: The amount of the payment.
			@param message: An optional message for the payment.
			@return A representation of the paymentRequest
			"""
			payment_id = Swish.generate_swish_id()
			print(f'Generarade id {payment_id}')
			
			json = {
				"payeeAlias": self.payee_alias,
				"callbackUrl": self.callback_url,
				"amount": amount,
				"message": message,
				"currency": "SEK",
			}

			payment_request_db_object = SwishPaymentRequestModel(id=payment_id, amount=amount)
			payment_request_db_object.save()

			payment_request_external_uri = None
			payment_request_token = None

			try:
				resp = requests.put(f'{self.swish_url}api/v2/paymentrequests/{payment_id}', json=json, cert=self.cert_file_paths)
				resp.raise_for_status()
				
				payment_request_external_uri = resp.headers["Location"]
				payment_request_token = resp.headers["PaymentRequestToken"]

				print(resp)
				print(resp.headers)
			except requests.exceptions.RequestException as e:
				# TODO LOG WARNING(/ERROR?). This should not happen unless there is a conficuration error.
				print(f'Error creating Swish payment: {e}')

				payment_request_db_object.fail(PaymentErrorCode.FAILED_TO_INITIATE)
				payment_request_db_object.save()

				self.callback_function(SwishPaymentRequest(payment_request_db_object))

			payment_request_db_object.token = payment_request_token
			payment_request_db_object.payment_request_external_uri = payment_request_external_uri 
			payment_request_db_object.save()

			return SwishPaymentRequest(payment_request_db_object)

	@staticmethod
	def get_instance():
		global instance
		if instance is None:
			raise Exception("Swish singleton has not been initialized!")

		return instance


def example_callback_handler_function(paymentRequest: SwishPaymentRequest):
	if paymentRequest.is_payed():
		print(f'Marking {paymentRequest.payment_id} as paid')
	elif paymentRequest.status == PaymentStatus.CANCELLED:
		print(f'Payment {paymentRequest.payment_id} failed because: {paymentRequest.status.name}')
	# Unclear if this exists since we do not know if swish can have a waiting status
	elif paymentRequest.status == PaymentStatus.WAITING:
		print(f'Payment {paymentRequest.payment_id} is waiting...')
