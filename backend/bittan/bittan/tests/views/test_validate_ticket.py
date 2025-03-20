from django.test import TestCase, Client

from django.utils import timezone

from bittan.models import ChapterEvent, TicketType, Ticket, Payment, chapter_event
from bittan.models.payment import PaymentStatus

class ValidateTicketTest(TestCase):
    def setUp(self):
        NOW = timezone.now()
        self.test_event = ChapterEvent.objects.create(title="Test Event", description="An event for testing. ", total_seats=10, sales_stop_at=NOW+timezone.timedelta(days=365), event_at=NOW)
        
        test_ticket = TicketType.objects.create(price=200, title="Test Ticket", description="A ticket for testing.")
        self.test_event.ticket_types.add(test_ticket)
        
        self.valid_payment = Payment.objects.create(
                expires_at=NOW + timezone.timedelta(hours=2),
                swish_id="testid",
                status=PaymentStatus.PAID,
                email="mail@mail.com",
                sent_email=True,
                payment_started=True
        )

        self.invalid_payment = Payment.objects.create(
                expires_at=NOW - timezone.timedelta(hours=2),
                swish_id="testid2",
                status=PaymentStatus.FAILED_EXPIRED_RESERVATION,
                email="mail@mail.com",
                sent_email=False,
                payment_started=False
        )

        self.valid_ticket = Ticket.objects.create(
                external_id="AAAAAA", 
                time_created=NOW,
                payment=self.valid_payment,
                ticket_type=test_ticket,
                chapter_event=self.test_event
        )
        
        self.invalid_ticket = Ticket.objects.create(
                external_id="BBBBBB", 
                time_created=NOW,
                payment=self.invalid_payment,
                ticket_type=test_ticket,
                chapter_event=self.test_event
        )

        self.client = Client()

    def test_validate_ticket(self):
        r1 = self.client.put(
                "/validate_ticket/",
                {
                    "external_id": "AAAAAA"
                },
                content_type="application/json"
        )

        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.data["times_used"], 0) 
        self.assertEqual(r1.data["status"], "PAID") 
        self.assertEqual(r1.data["chapter_event"], self.chapter_event1.title)

        r1 = self.client.put(
                "/validate_ticket/",
                {
                    "external_id": "AAAAAA"
                },
                content_type="application/json"
        )

        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.data["times_used"], 1) 
        self.assertEqual(r1.data["status"], "PAID") 


        r2 = self.client.put(
                "/validate_ticket/",
                {
                    "external_id": "BBBBBB"
                },
                content_type="application/json"
        )

        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.data["times_used"], 0) 
        self.assertEqual(r2.data["status"], "FAILED_EXPIRED_RESERVATION") 

    def test_nonexisting_ticket(self):
        r1 = self.client.put(
                "/validate_ticket/",
                {
                    "external_id": "QWERTY"
                },
                content_type="application/json"
        )

        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.data["times_used"], -1) 
        self.assertEqual(r1.data["status"], "Ticket does not exist") 

    def test_invalid_request(self):
        r1 = self.client.put(
                "/validate_ticket/",
                {
                    "id": "QWERTY"
                },
                content_type="application/json"
        )
        self.assertEqual(r1.status_code, 400)


