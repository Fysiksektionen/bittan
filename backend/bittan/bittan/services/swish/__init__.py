import requests

from bittan.models.payment import PaymentStatus
from ...models.swish_payment_request import SwishPaymentRequest, PaymentErrorCode
from enum import Enum
from uuid import uuid4

instance = None


def example_callback_handler_function(payment_id: str, SwishCallbackRequest):
	if SwishCallbackRequest.status:
		print(f'Marking {payment_id} as paid')
	else:
		print(f'Payment {payment_id} failed because: {status.name}')


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

		self.http_client = requests.cli

		global instance
		instance = self

	def sync_payment_request(payment_request: SwishPaymentRequest):
		pass


	def get_payment_status(id: str):
		payment_request = SwishPaymentRequest.objects.get(pk=id)
		if payment_request.status != PaymentStatus.WAITING:
			return payment_request.status

		payment_request.sync_with_swish()

		return payment_request.status 


	@staticmethod
	def generate_swish_id() -> str: 
		return str(uuid4()).replace('-', '').upper()

	def send_to_swish(method, path: str, data = None, **kwargs):
		requests.request(method, )	



 # Returnera (id, token)
	def create_swish_payment(self, payment_id: str, amount: int, message="") -> tuple[str, str|None]:
		json = {
			"payeeAlias": self.payee_alias,
			"callbackUrl": self.callback_url,
			"amount": amount,
			"message": message,
			"currency": "SEK",
		}

		payment_request_db_object = SwishPaymentRequest(id=id, amount=amount)
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

		payment_request_db_object.payment_request_db_object = payment_request_token
		payment_request_db_object.payment_request_external_uri = payment_request_external_uri 
		payment_request_db_object.save()

		return (payment_id, payment_request_token)

	@staticmethod
	def get_instance():
		global instance
		if instance is None:
			raise Exception("Swish singleton has not been initialized!")

		return instance