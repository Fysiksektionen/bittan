from django.test import TestCase, Client
from django.core.management import call_command
from django.utils import timezone
from unittest.mock import patch
import datetime
from bittan.models import TicketType, ChapterEvent, Payment, Ticket
from bittan.models.payment import PaymentStatus

MOCK_NOW = datetime.datetime(1970, 1, 1, tzinfo=timezone.timezone.utc)

@patch("django.utils.timezone.now", return_value=MOCK_NOW)
class CleanerTicketReservationIntegrationTest(TestCase):
	def setUp(self):
		self.res_dur = timezone.timedelta(minutes=10)

		self.ce1 = ChapterEvent.objects.create(
			title="Test event",
			description="An event for testing",
			total_seats=10,
			sales_stop_at=MOCK_NOW + timezone.timedelta(days=1),
			reservation_duration=timezone.timedelta(minutes=10),
			event_at=MOCK_NOW + timezone.timedelta(days=365)
		)

		self.test_ticket = TicketType.objects.create(
			title="Test ticket",
			price=100,
			description="A test ticket"
		)
		self.ce1.ticket_types.add(self.test_ticket)

		self.client = Client()

	def test_cleans_correctly(self, mock_now):
		reservation_res = self.client.post(
            "/reserve_ticket/", 
            {
                "chapter_event": str(self.ce1.pk),
                "tickets": [
                    {
                        "ticket_type": self.test_ticket.pk,
                        "count": 4
                        }
                    ]
            },
            content_type="application/json"
		)

		if reservation_res.status_code != 201:
			raise Exception("Failed to perform reservation of tickets in preparation for testing test_expired_session_out_of_tickets.")

		call_command("run_cleaner")

		payment_id = self.client.session["reserved_payment"]
		payment = Payment.objects.get(pk=payment_id)

		self.assertEqual(payment.status, PaymentStatus.RESERVED, "Payment was cleaned when still alive. ")
		 
		mock_now.return_value = MOCK_NOW + self.res_dur + timezone.timedelta(minutes=1)

		call_command("run_cleaner")
		payment = Payment.objects.get(pk=payment_id)
		self.assertEqual(payment.status, PaymentStatus.FAILED_EXPIRED_RESERVATION, "Payment was not cleaned when expected. ")
	
	def test_ignores_payment_started(self, mock_now):
		reservation_res = self.client.post(
            "/reserve_ticket/", 
            {
                "chapter_event": str(self.ce1.pk),
                "tickets": [
                    {
                        "ticket_type": self.test_ticket.pk,
                        "count": 4
                        }
                    ]
            },
            content_type="application/json"
		)

		if reservation_res.status_code != 201:
			raise Exception("Failed to perform reservation of tickets in preparation for testing test_expired_session_out_of_tickets.")

		payment_id = self.client.session["reserved_payment"]

		_ = self.client.post(
            "/start_payment/",
            {
				"email_address": "mail@mail.com"
			}
		)

		mock_now.return_value = MOCK_NOW + self.res_dur + timezone.timedelta(minutes=1)
		call_command("run_cleaner")
		payment = Payment.objects.get(pk=payment_id)
		self.assertEqual(payment.status, PaymentStatus.RESERVED, "Payment was cleaned when it was started.")
		pass


class RunCleanerTest(TestCase):
	def setUp(self):		
		NOW = timezone.now()
		# slowticket = TicketType.objects.create(price=100, title="Slow ticket", description="Ticket that expires slowly.", reservation_duration=datetime.timedelta(hours=1))
		# fastticket = TicketType.objects.create(price=100, title="Fast ticket", description="Ticket that expires quickly.", reservation_duration=datetime.timedelta(milliseconds=1))
		# chapter_event1 = ChapterEvent.objects.create(title="Fysikalen Dag 1", description="Första dagen av Fysikalen.", max_tickets=10, sales_stop_at=NOW+datetime.timedelta(days=365))
		# chapter_event1.ticket_types.add(slowticket, fastticket)

		# TODO use Gabriel's function to create payments
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

	def test_disable_multiple(self):
		NOW = timezone.now()
		self.payment_expires_now2_id = Payment.objects.create(
			expires_at = NOW,
			swish_id = "abc",
			status = PaymentStatus.RESERVED,
			email = "abc"
		).id
		call_command("run_cleaner")
		self.assertEqual(
			Payment.objects.filter(id=self.payment_expires_now_id).get().status,
			PaymentStatus.FAILED_EXPIRED_RESERVATION
		)
		self.assertEqual(
			Payment.objects.filter(id=self.payment_expires_now2_id).get().status,
			PaymentStatus.FAILED_EXPIRED_RESERVATION
		)
