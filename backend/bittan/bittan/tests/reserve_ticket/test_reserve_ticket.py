from django.test import TestCase, Client

from django.utils import timezone

from bittan.models import TicketType, ChapterEvent

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
        self.assertEqual(response.status_code, 201, "/reserve_ticket/ did not return status code 201 correctly. ")
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
        
    def test_negative_tickets(self):
        response = self.client.post(
            "/reserve-ticket/", 
            {
                "chapter_event": str(self.test_event.pk),
                "tickets": [
                    {
                        "ticket_type": "Test Ticket",
                        "count": -1
                    },
                    {
                        "ticket_type": "Test Ticket 2",
                        "count": 0
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_nonexisting_chapter_event(self):
        event_id: int = 9999 if self.test_event.pk != 9999 else 1
        response = self.client.post(
               "/reserve-ticket/", 
            {
                "chapter_event": event_id,
                "tickets": [
                    {
                        "ticket_type": "Test Ticket",
                        "count": 1
                    },
                    {
                        "ticket_type": "Test Ticket 2",
                        "count": 1
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

    def test_nonexisting_ticket_type(self):
        response = self.client.post(
               "/reserve-ticket/", 
            {
                "chapter_event": self.test_event.pk,
                "tickets": [
                    {
                        "ticket_type": "No Ticket",
                        "count": 1
                    },
                    {
                        "ticket_type": "Test Ticket 2",
                        "count": 1
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404, "/reserve-ticket did not return status 404 when reserving non-existent ticket. ")

        response = self.client.post(
               "/reserve-ticket/", 
            {
                "chapter_event": self.test_event.pk,
                "tickets": [
                    {
                        "ticket_type": "Secret ticket",
                        "count": 1
                    },
                    {
                        "ticket_type": "Test Ticket 2",
                        "count": 1
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404, "/reserve-ticket did not return status 404 when reserving secret ticket. ")

    def test_invalid_json_format(self):
        response = self.client.post(
               "/reserve-ticket/", 
            {
                "chapter_event": self.test_event.pk,
                "tickets": [
                    {
                        "ticket_type": "No Ticket",
                        "count": 1
                    },
                    {
                        "ticket_type": "Test Ticket 2",
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
