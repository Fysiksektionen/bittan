from django.test import TestCase, Client

from django.utils import timezone

from bittan.models import TicketType, ChapterEvent

class ReserveTicketTest(TestCase):
    def setUp(self):
        NOW = timezone.now()
        test_ticket = TicketType.objects.create(price=199.99, title="Test Ticket", description="A ticket for testing.")
        self.test_event = ChapterEvent.objects.create(title="Test Event", description="An event for testing. ", max_tickets=10, sales_stop_at=NOW+datetime.timedelta(days=365))
        self.test_event.ticket_types.add(test_ticket)

        self.client = Client()
    
    def test_reserve_ticket(self):
        response = self.client.post(
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
        self.assertEqual(response.status_code, 200, "/reserve_ticket/ did not return status code 200 correct. ")
        self.assertIsNotNone(response.cookies.get("sessionid", None), "/reserve_ticket/ did not give a session cookie. ")

    
    def test_out_of_tickets(self):
        response = self.client.post(
            "/reserve-ticket/", 
            {
                "chapter_event": str(self.test_event.pk),
                "tickets": [
                    {
                        "ticket_type": "Test Ticket",
                        "count": 11
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
        
