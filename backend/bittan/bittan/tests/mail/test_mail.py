from django.test import TestCase, tag
from bittan.mail import send_mail
from bittan.mail import MailError, InvalidRecieverAddressError
from bittan.mail import mail_ticket

class LeoTest(TestCase):

	def test_leo(self):
		mail_ticket("bittantest@gmail.com")

@tag("no_ci")
class SendMailTest(TestCase):

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

class QRCodeTest(TestCase):
	# TODO refactor this with the new qr code creation

	def setUp(self):
		pass

	def test_make_qr_image(self):
		qr = make_qr_image("This is some content!")
		self.assertEqual(type(qr), bytes)
		self.assertGreater(len(qr), 1)

	@tag("no_ci")
	def test_send_qr_in_mail(self):
		qr = make_qr_image("This is some content!")
		send_mail("bittantest@gmail.com", "QR Test", "This test mail contains a QR code.", qr)
