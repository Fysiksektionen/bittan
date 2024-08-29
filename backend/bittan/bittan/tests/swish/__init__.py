from uuid import uuid4
from bittan.services.swish import Swish, example_callback_handler_function
from django.test import TestCase
import requests

class FirstTestCase(TestCase):
	def setUp(self):
		pass

	def test_swish_instance():
		url = f'https://mss.cpc.getswish.net/swish-cpcapi/api/v2/paymentrequests'
		callback_url = "https://cab4-2001-6b0-1-1041-9825-49e0-597b-5858.ngrok-free.app/swish/callback"
		cert_file_paths = ("./test_certificates/testcert.pem", "./test_certificates/testcert.key")
		

		swish = Swish(url, "1234679304", callback_url, cert_file_paths, example_callback_handler_function)
		swish.create_swish_payment(Swish.generate_swish_id(), 123)
