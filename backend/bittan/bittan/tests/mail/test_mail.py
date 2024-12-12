from django.test import TestCase, tag
from bittan.mail import send_mail
from bittan.mail import MailError, InvalidRecieverAddressError
from bittan.mail import mail_ticket
from bittan.models.payment import Payment, PaymentStatus
from bittan.models.ticket import Ticket
from bittan.models.ticket_type import TicketType

class LeoTest(TestCase):

	def test_leo(self):
		NOW = datetime.datetime.now()

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
					ticket_type = standardbiljett
				)
		ticket2 = Ticket.objects.create(
					external_id = "GHIJKL",
					time_created = NOW,
					payment = payment1,
					ticket_type = standardbiljett
				)
		ticket3 = Ticket.objects.create(
					external_id = "MNOPQR",
					time_created = NOW,
					payment = payment1,
					ticket_type = seniorbiljett
				)

		mail_ticket(payment1)

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
