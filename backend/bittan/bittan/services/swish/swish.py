import logging
from django.apps import apps
from django.dispatch import Signal
import requests
import json

from ...models.swish_payment_request import SwishPaymentRequestModel, PaymentErrorCode as SwishApiErrorCode, PaymentStatus as SwishApiPaymentStatus
from .swish_payment_request import SwishPaymentRequest

from uuid import uuid4

payment_signal = Signal()

class SwishPaymentRequestResponse: 
	""" This is the response that the official swish api sends after we have sent a request """ 
	status: SwishApiPaymentStatus
	error_code: SwishApiErrorCode 
	id: str 

	def __init__(self, response):
		self.id = response['id']
		self.status = SwishApiPaymentStatus.from_swish_api_status(response['status'])
		self.error_code = SwishApiErrorCode.from_swish_reponse_code(response['errorCode'])

class Swish:
	def __init__(self, swish_url, payee_alias, callback_url, cert_file_paths):
		self.swish_url = swish_url
		self.payee_alias = payee_alias
		self.callback_url = callback_url
		self.cert_file_paths = cert_file_paths


	def update_swish_payment_request(self, payment_request_response: dict, model: SwishPaymentRequestModel | None = None):
		""" Updates a payment according to a response (payment_request_response) from the Swish api """
		
		# We are going to store the raw response data in our model, incase something bad happens and manual analysis
		response_raw = json.dumps(payment_request_response)

		payment_request_response = SwishPaymentRequestResponse(payment_request_response)
		if model is None:
			model = SwishPaymentRequestModel.objects.get(pk=payment_request_response.id)

		model.date_paid = payment_request_response.get("datePaid")

		send_callback = False
		# TODO Check that it makes sense to only call the callback on status change
		# Only send a callback to the callback handler if the status has been changed
		if model.status != payment_request_response.status:
			send_callback = True

		model.error_code = payment_request_response.error_code
		model.status = payment_request_response.status

		model.swish_api_response = response_raw
		model.save()

		if send_callback:
			payment_request = SwishPaymentRequest(model)
			self.notify_listeners(payment_request)

		return model

	def notify_listeners(self, payment_request: SwishPaymentRequest):
		payment_signal.send(Swish, payment_request=payment_request)

	def synchronize_all_pending(self):
		pending_payments = SwishPaymentRequestModel.objects.filter(status=SwishApiPaymentStatus.CREATED)

		for pending in pending_payments:
			self.synchronize_payment_request(pending)

	def synchronize_payment_request(self, payment_request: SwishPaymentRequestModel | str):
		""" This method is useful for when the callbacks are not working. It fetches the state of a payment via the swish api and updates our local info on the payment """

		payment_request_id = None
		if isinstance(payment_request, str):
			payment_request_id = payment_request 
			payment_request = None
		else:
			payment_request_id = payment_request.id

		response = self.send_to_swish('GET', f'api/v1/paymentrequests/{payment_request_id}')
		if response.status_code != 200:
			# TODO Handle errors more elegantly, this should NOT happen!
			logging.error("PaymentRequestDoes not exist:", payment_request_id)

			raise Exception("There is no swish payment request with the id ", swish_payment_request)
		
		response_body = response.json()
		return self.update_swish_payment_request(response_body, payment_request)


	def cancel_payment(self, payment_id: str):
		""" 
		Retracts a payment request so that a user is unable to pay it if it has not already been paid. If the payment already is paid, nothing happens.
		return true if the payment was able to be cancelled, false otherwise
		"""
		headers = {'Content-Type': 'application/json-patch+json'}

		payment_request = SwishPaymentRequestModel.objects.get(pk=payment_id)

		if payment_request.status != SwishApiPaymentStatus.CREATED:
			return False

		body = [{
			"op": "replace",
			"path": "/status",
			"value": "cancelled"
		}]

		response = self.send_to_swish("PATCH", f'api/v1/paymentrequests/{payment_request.id}',headers=headers, json=body)
		if not response.ok:
			# Our internal payment status does not match the payment status that swish has.
			logging.warn(f'Payment {payment_id} was not able to be cancelled, however it should be cancellable.')
			self.synchronize_payment_request(payment_id)
			return False

		# Note: We do not have to update the payment status if we are able to cancel the payment since swish will send a callback to 
		# our callback endpoint which inturn will update the payment status. 
		return True

	def get_payment_request(self, id: str) -> SwishPaymentRequest:
		payment_request = SwishPaymentRequestModel.objects.get(pk=id)

		# TODO check that payment requests only can change state once	
		# If the payment status is created, there is a chance that it's status has been changed
		if payment_request.status == SwishApiPaymentStatus.CREATED:
			self.synchronize_payment_request(payment_request)

		return SwishPaymentRequest(payment_request)


	@staticmethod
	def generate_swish_id() -> str: 
		""" We have to provide an id when creating swish payment requests, this method generates valid id:s """
		return str(uuid4()).replace('-', '').upper()
	
	def handle_swish_callback(self, response):
		self.update_swish_payment_request(response)

	def send_to_swish(self, method, path: str, **kwargs):
		""" Convenience method for sending an HTTP request to the SWISH api """

		endpoint = f'{self.swish_url}/{path}'
		return requests.request(method, endpoint, cert=self.cert_file_paths, **kwargs)


	def create_swish_payment(self, amount: int, message="") -> SwishPaymentRequest:
			"""
			Tells Swish that we want to create a payment. 

			@param amount: The amount of the payment.
			@param message: An optional message for the payment.
			@return A representation of the paymentRequest
			"""
			payment_id = Swish.generate_swish_id()
			

			payment_request_db_object = SwishPaymentRequestModel(id=payment_id, amount=amount)
			payment_request_db_object.save()

			json = {
				"payeePaymentReference": self.payee_alias,
				"payeeAlias": self.payee_alias,
				"callbackUrl": self.callback_url,
				"amount": amount,
				"message": message,
				"currency": "SEK",
			}
			resp = self.send_to_swish('PUT', f'api/v2/paymentrequests/{payment_id}', json=json)


			try:
				resp.raise_for_status()

				payment_request_external_uri = resp.headers["Location"]
				payment_request_token = resp.headers["PaymentRequestToken"]

				payment_request_db_object.token = payment_request_token
				payment_request_db_object.external_uri = payment_request_external_uri 
			except requests.exceptions.RequestException as e:
				# TODO This should not happen unless there is a configuration error, or if we have connectivity problems. Handle more gracefully? 
				logging.error(f'Error creating Swish payment: {e}')

				# The data is, unlike the "happy path", in the body as json if the request fails 
				payment_request_db_object.swish_api_response = e.response.text

				payment_request_db_object.fail(SwishApiErrorCode.FAILED_TO_INITIATE)
				payment_request_db_object.save()

				self.notify_listeners(SwishPaymentRequest(payment_request_db_object))



			# Yes, swish sends the data in the headers for this response, keep this in mind if debugging.
			payment_request_db_object.swish_api_response = resp.headers 

			payment_request_db_object.save()

			return SwishPaymentRequest(payment_request_db_object)

	@staticmethod
	def get_instance():
		instance = apps.get_app_config('bittan').swish
		return instance 
