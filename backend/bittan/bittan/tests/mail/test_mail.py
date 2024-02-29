from django.test import TestCase
from bittan.mail import send_mail
from bittan.mail import MailError, InvalidRecieverAddressError

class MailTest(TestCase):

	def setUp(self):
		pass

	def test_send_mail(self):
		send_mail("bittantest@gmail.com", "Test", "This is sent by a test.")

	def test_invalid_address(self):
		self.assertRaises(
			InvalidRecieverAddressError,
			lambda : send_mail("some invalid address", "Test", "This is sent by a test.")
		)
		self.assertRaises(
			MailError,
			lambda : send_mail("some invalid address", "Test", "This is sent by a test.")
		)
