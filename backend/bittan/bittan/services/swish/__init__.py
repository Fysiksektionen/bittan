import requests

from bittan.models.payment import PaymentStatus
from ...models.swish_payment_request import SwishPaymentRequestModel, PaymentErrorCode
from enum import Enum
from uuid import uuid4
from datetime import datetime

class SwishApiStatus(Enum):
	PAID = "PAID"
	CANCELLED = "CANCELLED"
	WAITING = "WAITING"

class SwishApiErrorCode(Enum):
	def __str__(self):
		return self.name

	@classmethod
	def from_swish_response_code(cls, code: str):
		for member in cls:
			if member.value == code:
				return member
		return None


instance = None
class SwishPaymentRequestResponse():
	""" Our representation of Swish:s representation of a payment request.

	The spec for a payment request can be found on the swish docs for the [payment request object](https://developer.swish.nu/api/payment-request/v2#payment-request-object)
	"""
	id: str
	payeePaymentReference: str
	paymentReference: str | None
	
	callbackUrl: str
	callbackIdentifier: str | None

	payerAlias:  str | None
	payeeAlias: str  | None

	# Oklart vilken typ
	ammount: str | int 
	currency: str

	message: str
	status: SwishApiStatus

	dateCreated: datetime 
	datePaid: datetime | None

	errorCode: SwishApiErrorCode | None
	errorMessage: str | None
	
	status: SwishApiStatus
	errorCode: PaymentErrorCode

	def __init__(self, data: dict):
		self.all_data_str = str(data)
		self.status = SwishApiStatus.PAID 
		self.id = data.id
		self.errorCode = None

		if data.get('status') != 'PAID':
			# TODO kan den wara WAITING också?
			self.status = PaymentStatus.CANCELLED

			# TODO FIX
			# self.errorCode = PaymentErrorCode.from_swish_reponse_code(data.get('errorCode'))

class SwishPaymentRequest:
	"""A class that represents all the user of this api needs to know about a payment"""
	
	def __init__(self, paymentRequest: SwishPaymentRequestModel):
		self.id = paymentRequest.id
		self.status = paymentRequest.status
		self.errorCode = paymentRequest.errorCode
		self.swish_token = paymentRequest.swish_token
		
	def is_payed(self):
		return self.status == PaymentStatus.PAID
	
	id: str

	status: PaymentStatus 
	errorCode: PaymentErrorCode | None

	# Used to start the swish app. Used by the frontent to make the payment
	swish_token: str | None
class Swish():
	# GetSwish payment med status funktion
	# Callback grej
	# Get token
	def __init__(self, swish_url, payee_alias, callback_url, cert_file_paths, callback_function):
		self.swish_url = swish_url
		self.payee_alias = payee_alias
		self.callback_url = callback_url
		self.payeee_reference_id = ""
		self.cert_file_paths = cert_file_paths

		self.callback_function = callback_function


		global instance
		instance = self

	def update_swish_payment_request(payment_request: SwishPaymentRequestResponse):
		model = SwishPaymentRequestModel.objects.get(pk=payment_request.id)
		# TODO

	def synchronize_payment_request(payment_request: SwishPaymentRequestModel):
		# TODO
		# Call GET swishpayment request
		# Save using swish_payment_request
		pass

	def get_payment_request(self, id: str):
		payment_request = SwishPaymentRequestModel.objects.get(pk=id)
		if payment_request.status != PaymentStatus.WAITING:
			return payment_request.status

		self.synchronize_payment_request(payment_request)
		return payment_request.status 


	@staticmethod
	def generate_swish_id() -> str: 
		return str(uuid4()).replace('-', '').upper()

	def send_to_swish(self, method, path: str, data = None, **kwargs):
		return requests.request(method, f'{self.swish_url}/{path}', cert=self.cert_file_paths, **kwargs)


 # Returnera (id, token)
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
				resp = requests.put(f'{self.swish_url}/{payment_id}', json=json, cert=self.cert_file_paths)
				resp.raise_for_status()
				
				payment_request_external_uri = resp.headers["Location"]
				payment_request_token = resp.headers["PaymentRequestToken"]

				print(resp)
				print(resp.headers)
			except requests.exceptions.RequestException as e:
				# TODO Send callback
				payment_request_db_object.fail(PaymentErrorCode.FAILED_TO_INITIATE)
				print(f'Error creating Swish payment: {e}')
				# Handle the error here


			payment_request_db_object.swish_token = payment_request_token
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
	else:
		print(f'Payment {paymentRequest.payment_id} failed because: {paymentRequest.status.name}')