from django.test import TestCase
from django.core.management import call_command
import datetime
import time
from bittan.models import TicketType, ChapterEvent, Payment, Ticket
from bittan.models.payment import PaymentStatus

class RunCleanerTest(TestCase):

	def setUp(self):		
		NOW = datetime.datetime.now()
		# slowticket = TicketType.objects.create(price=100, title="Slow ticket", description="Ticket that expires slowly.", reservation_duration=datetime.timedelta(hours=1))
		# fastticket = TicketType.objects.create(price=100, title="Fast ticket", description="Ticket that expires quickly.", reservation_duration=datetime.timedelta(milliseconds=1))
		# chapter_event1 = ChapterEvent.objects.create(title="Fysikalen Dag 1", description="Första dagen av Fysikalen.", max_tickets=10, sales_stop_at=NOW+datetime.timedelta(days=365))
		# chapter_event1.ticket_types.add(slowticket, fastticket)

		# TODO use Gabriel's function to create payments
		# TODO maybe reservation_duration should depend on chapter_event
		self.payment_expires_now_id = Payment.objects.create(
			expires_at = NOW,
			swish_id = "abc",
			status = PaymentStatus.RESERVED,
			email = "abc"
		).id
		self.payment_expires_future_id = Payment.objects.create(
			expires_at = NOW + datetime.timedelta(minutes=5),
			swish_id = "abc",
			status = PaymentStatus.RESERVED,
			email = "abc"
		).id
		self.payment_paid_id = Payment.objects.create(
			expires_at = NOW,
			swish_id = "abc",
			status = PaymentStatus.PAID,
			email = "abc"
		).id
		self.payment_started_id = Payment.objects.create(
			expires_at = NOW,
			swish_id = "abc",
			status = PaymentStatus.RESERVED,
			email = "abc",
			payment_started=True
		).id

	def test_disables_expired(self):
		self.assertEqual(
			Payment.objects.filter(id=self.payment_expires_now_id).get().status,
			PaymentStatus.RESERVED
		)
		call_command("run_cleaner")
		self.assertEqual(
			Payment.objects.filter(id=self.payment_expires_now_id).get().status,
			PaymentStatus.FAILED_EXPIRED_RESERVATION
		)

	def test_ignores_expires_future(self):
		self.assertEqual(
			Payment.objects.filter(id=self.payment_expires_future_id).get().status,
			PaymentStatus.RESERVED
		)
		call_command("run_cleaner")
		self.assertEqual(
			Payment.objects.filter(id=self.payment_expires_future_id).get().status,
			PaymentStatus.RESERVED
		)

	def test_ignores_paid(self):
		self.assertEqual(
			Payment.objects.filter(id=self.payment_paid_id).get().status,
			PaymentStatus.PAID
		)
		call_command("run_cleaner")
		self.assertEqual(
			Payment.objects.filter(id=self.payment_paid_id).get().status,
			PaymentStatus.PAID
		)

	def test_ignores_payment_started(self):
		self.assertEqual(
			Payment.objects.filter(id=self.payment_started_id).get().status,
			PaymentStatus.RESERVED
		)
		call_command("run_cleaner")
		self.assertEqual(
			Payment.objects.filter(id=self.payment_started_id).get().status,
			PaymentStatus.RESERVED
		)
