from bittan.models.payment import PaymentStatus
from unittest.mock import patch
from django.test import TestCase, Client

from datetime import datetime
from django.utils import timezone

from bittan.models import TicketType, ChapterEvent, Ticket, Payment

class StartPaymentTest(TestCase):
    def setUp(self):
        NOW = timezone.now()
        self.test_event = ChapterEvent.objects.create(title="Test Event1", description="An event for testing. ", total_seats=10, sales_stop_at=NOW+timezone.timedelta(days=365), event_at=NOW+timezone.timedelta(days=366))
        self.test_event2 = ChapterEvent.objects.create(title="Test Event2", description="An event for testing. ", total_seats=10, sales_stop_at=NOW+timezone.timedelta(days=365), event_at=NOW+timezone.timedelta(days=366), reservation_duration=timezone.timedelta(minutes=30))
        
        self.test_ticket = TicketType.objects.create(price=200, title="Test Ticket", description="A ticket for testing.")
        self.test_event.ticket_types.add(self.test_ticket)
        
        self.test_ticket2 = TicketType.objects.create(price=100, title="Test Ticket 2", description="A ticket for testing number 2.")
        self.test_event.ticket_types.add(self.test_ticket2)

        self.secret_ticket = TicketType.objects.create(price=0, title="Secret Ticket", description="A free ticket (very secret)", is_visible=False)
        self.test_event.ticket_types.add(self.secret_ticket)

        self.client = Client()

        self.reservation_response = self.client.post(
            "/reserve_ticket/", 
            {
                "chapter_event": str(self.test_event.pk),
                "tickets": [
                    {
                        "ticket_type": self.test_ticket.pk,
                        "count": 4
                        }
                    ]
            },
            content_type="application/json"
        )

        # Temporary setup as the reserve_ticket view does not support reserving tickets for several different ChapterEvents at once. 
        payment_id = self.client.session["reserved_payment"]
        payment = Payment.objects.get(pk=payment_id)
        second_event_ticket1 =  Ticket.objects.create(
            external_id = "1234",
            time_created = NOW,
            payment = payment,
            ticket_type = self.test_ticket,
            chapter_event = self.test_event2
        )
        second_event_ticket2 =  Ticket.objects.create(
            external_id = "1111",
            time_created = NOW,
            payment = payment,
            ticket_type = self.test_ticket2,
            chapter_event = self.test_event2
        )



    def test_start_payment(self):
        mail_address = "mail@mail.com"
        response = self.client.post(
            "/start_payment/",
            {
                "email_address": mail_address
            }
        )

        self.assertEqual(response.status_code, 200)
        payment_id = self.client.session["reserved_payment"]
        payment = Payment.objects.get(pk=payment_id)
        self.assertEqual(payment.payment_started, True)
        self.assertEqual(payment.email, mail_address)
        self.assertEqual(payment.status, PaymentStatus.RESERVED)
    
    def test_invalid_mail(self):
        response = self.client.post(
            "/start_payment/",
            {
                "email_address": "dsjklasdfljka"
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_session_token(self):
        new_client = Client()
        response = new_client.post(
            "/start_payment/",
            {
                "email_address": "mail@mail.com"
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_expired_session_out_of_tickets(self):
        payment_id = self.client.session["reserved_payment"]
        payment = Payment.objects.get(pk=payment_id)
        payment.status = PaymentStatus.FAILED_EXPIRED_RESERVATION
        payment.save()

        client2 = Client()
        prep_res = client2.post(
            "/reserve_ticket/", 
            {
                "chapter_event": str(self.test_event.pk),
                "tickets": [
                    {
                        "ticket_type": self.test_ticket.pk,
                        "count": 8
                        }
                    ]
            },
            content_type="application/json"
        )

        if prep_res.status_code != 201:
            raise Exception("Failed to perform reservation of tickets in preparation for testing test_expired_session_out_of_tickets.")

        response = self.client.post(
            "/start_payment/",
            {
                "email_address": "mail@mail.com"
            }
        )
        self.assertEqual(response.status_code, 408) 
        payment_id = self.client.session["reserved_payment"]
        payment = Payment.objects.get(pk=payment_id)
        self.assertEqual(payment.status, PaymentStatus.FAILED_EXPIRED_RESERVATION)
        self.assertEqual(payment.payment_started, False)

    @patch('django.utils.timezone.now')
    def test_expired_session_rebook_tickets(self, mock_now):
        now = datetime(1970, 1, 1, tzinfo=timezone.timezone.utc)
        mock_now.return_value = now

        payment_id = self.client.session["reserved_payment"]
        payment = Payment.objects.get(pk=payment_id)
        payment.status = PaymentStatus.FAILED_EXPIRED_RESERVATION
        payment.save()

        mail_address = "mail@mail.com"
        response = self.client.post(
            "/start_payment/",
            {
                "email_address": mail_address
            }
        )

        payment_id = self.client.session["reserved_payment"]
        payment = Payment.objects.get(pk=payment_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payment.payment_started, True)
        self.assertEqual(payment.email, mail_address)
        self.assertEqual(payment.status, PaymentStatus.RESERVED)
        self.assertEqual(payment.expires_at, now + self.test_event2.reservation_duration)

    def test_double_payment(self):
        mail_address = "mail@mail.com"
        response = self.client.post(
            "/start_payment/",
            {
                "email_address": mail_address
            }
        )

        response = self.client.post(
            "/start_payment/",
            {
                "email_address": mail_address
            }
        )

        payment_id = self.client.session["reserved_payment"]
        payment = Payment.objects.get(pk=payment_id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(payment.payment_started, True)
        self.assertEqual(payment.email, mail_address)
        self.assertEqual(payment.status, PaymentStatus.RESERVED)

