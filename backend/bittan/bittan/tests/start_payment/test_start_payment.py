from bittan.models.payment import PaymentStatus
from django.test import TestCase, Client
from django.contrib.sessions.backends.db import SessionStore

from django.utils import timezone

from bittan.models import TicketType, ChapterEvent, Payment

class ReserveTicketTest(TestCase):
    def setUp(self):
        NOW = timezone.now()
        self.test_event = ChapterEvent.objects.create(title="Test Event", description="An event for testing. ", max_tickets=10, sales_stop_at=NOW+timezone.timedelta(days=365))
        
        test_ticket = TicketType.objects.create(price=200, title="Test Ticket", description="A ticket for testing.")
        self.test_event.ticket_types.add(test_ticket)
        
        test_ticket2 = TicketType.objects.create(price=100, title="Test Ticket 2", description="A ticket for testing number 2.")
        self.test_event.ticket_types.add(test_ticket2)

        secret_ticket = TicketType.objects.create(price=0, title="Secret Ticket", description="A free ticket (very secret)", is_visible=False)
        self.test_event.ticket_types.add(secret_ticket)

        self.client = Client()

        self.reservation_response = self.client.post(
            "/reserve-ticket/", 
            {
                "chapter_event": str(self.test_event.pk),
                "tickets": [
                    {
                        "ticket_type": "Test Ticket",
                        "count": 1
                        }
                    ]
            },
            content_type="application/json"
        )

    def test_start_payment(self):
        response = self.client.post(
            "/start-payment/",
            {
                "email_address": "mail@mail.com"
            }
        )

        self.assertEqual(response.status_code, 200)
    
    def test_invalid_mail(self):
        response = self.client.post(
            "/start-payment/",
            {
                "email_address": "dsjklasdfljka"
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_no_session(self):
        new_client = Client()
        response = new_client.post(
            "/start-payment/",
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
        _ = client2.post(
            "/reserve-ticket/", 
            {
                "chapter_event": str(self.test_event.pk),
                "tickets": [
                    {
                        "ticket_type": "Test Ticket",
                        "count": 10
                        }
                    ]
            },
            content_type="application/json"
        )

        response = self.client.post(
            "/start-payment/",
            {
                "email_address": "mail@mail.com"
            }
        )
        self.assertEqual(response.status_code, 403) 

    def test_expired_session_rebook_tickets(self):
        payment_id = self.client.session["reserved_payment"]
        payment = Payment.objects.get(pk=payment_id)
        payment.status = PaymentStatus.FAILED_EXPIRED_RESERVATION

        response = self.client.post(
            "/start-payment/",
            {
                "email_address": "mail@mail.com"
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_double_payment(self):
        response = self.client.post(
            "/start-payment/",
            {
                "email_address": "mail@mail.com"
            }
        )

        response = self.client.post(
            "/start-payment/",
            {
                "email_address": "mail@mail.com"
            }
        )

        self.assertEqual(response.status_code, 403)


 
