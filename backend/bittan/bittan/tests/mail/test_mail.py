import datetime
from django.test import TestCase, tag
from django.utils import timezone
from bittan.mail import send_mail, mail_payment
from bittan.mail import MailError, InvalidReceiverAddressError
from bittan.mail.stylers import make_qr_image
from bittan.mail.mail import MailImage
from bittan.models.chapter_event import ChapterEvent
from bittan.models.payment import Payment, PaymentStatus
from bittan.models.ticket import Ticket
from bittan.models.ticket_type import TicketType

@tag("no_ci")
class SendMailTest(TestCase):

	def setUp(self):
		pass

	def test_send_mail(self):
		send_mail("bittantest@gmail.com", "Test", "This is sent by a test.", format_as_html=False)

	def test_invalid_address(self):
		self.assertRaises(
			InvalidReceiverAddressError,
			lambda : send_mail("some invalid address", "Test", "This is sent by a test.", format_as_html=False)
		)
		self.assertRaises(
			MailError,
			lambda : send_mail("some invalid address", "Test", "This is sent by a test.", format_as_html=False)
		)

class StylersTest(TestCase):

	def test_make_qr_image(self):
		qr = make_qr_image("Cool content", "Cool title")
		self.assertEqual(type(qr), bytes)
		self.assertGreater(len(qr), 1)

	@tag("no_ci")
	def test_send_mail_with_qr(self):
		imagebytes = make_qr_image("Cool content", "Cool title")
		images_to_attach = [MailImage(imagebytes=imagebytes, filename="qr")]
		images_to_embed = [MailImage(imagebytes=imagebytes, filename=f"qr_embed")]
		message = """<html>This test mail contains a QR code. <img src="cid:qr_embed"></html>"""
		send_mail("bittantest@gmail.com", "QR Test", message, images_to_attach, images_to_embed)

	@tag("no_ci")
	def test_mail_payment(self):
		NOW = timezone.now()

		standardbiljett = TicketType.objects.create(price=200, title="Standardbiljett", description="En vanlig biljett.")
		studentbiljett = TicketType.objects.create(price=100, title="Studentbiljett", description="En billigare biljett.")
		seniorbiljett = TicketType.objects.create(price=150, title="Seniorbiljett", description="En senior biljett.")

		chapter_event1 = ChapterEvent.objects.create(title="Fysikalen Dag 1", description="Första dagen av Fysikalen.", total_seats=10, sales_stop_at=NOW+datetime.timedelta(days=365), event_at=NOW+datetime.timedelta(days=365))
		chapter_event1.ticket_types.add(standardbiljett, studentbiljett, seniorbiljett)

		payment1 = Payment.objects.create(
					expires_at = NOW + datetime.timedelta(hours=1),
					swish_id = "Hej",
					status = PaymentStatus.PAID,
					email = "bittantest@gmail.com",
					sent_email = False
				)

		ticket1 = Ticket.objects.create(
					external_id = "ABCDEF",
					time_created = NOW,
					payment = payment1,
					ticket_type = standardbiljett,
					chapter_event=chapter_event1
				)
		ticket2 = Ticket.objects.create(
					external_id = "GHIJKL",
					time_created = NOW,
					payment = payment1,
					ticket_type = studentbiljett,
					chapter_event=chapter_event1
				)
		ticket3 = Ticket.objects.create(
					external_id = "MNOPQR",
					time_created = NOW,
					payment = payment1,
					ticket_type = seniorbiljett,
					chapter_event=chapter_event1
				)

		mail_payment(payment1)
		self.assertEqual(payment1.sent_email, True)
