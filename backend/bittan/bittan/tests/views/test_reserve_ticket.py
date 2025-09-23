from bittan.models.payment import Payment, PaymentStatus
from django.test import TestCase, Client

from django.utils import timezone

from bittan.models import TicketType, ChapterEvent

class ReserveTicketTest(TestCase):
    def setUp(self):
        NOW = timezone.now()
        self.test_event = ChapterEvent.objects.create(
                title="Test Event", 
                description="An event for testing. ", 
                total_seats=10, 
                max_tickets_per_payment = 8,
                sales_stop_at=NOW+timezone.timedelta(days=365), 
                event_at=NOW+timezone.timedelta(days=366)
            )
        
        self.test_ticket = TicketType.objects.create(price=200, title="Test Ticket", description="A ticket for testing.")
        self.test_event.ticket_types.add(self.test_ticket)
        
        self.test_ticket2 = TicketType.objects.create(price=100, title="Test Ticket 2", description="A ticket for testing number 2.")
        self.test_event.ticket_types.add(self.test_ticket2)

        self.secret_ticket = TicketType.objects.create(price=0, title="Secret Ticket", description="A free ticket (very secret)", is_visible=False)
        self.test_event.ticket_types.add(self.secret_ticket)

        self.client = Client()
    
    def test_reserve_ticket(self):
        response = self.client.post(
            "/reserve_ticket/", 
            {
                "chapter_event": str(self.test_event.pk),
                "tickets": [
                    {
                        "ticket_type": self.test_ticket.pk,
                        "count": 1
                    }
                ]
            },
            content_type="application/json"
        )
        payment_pk = Payment.objects.first().pk
        self.assertEqual(response.status_code, 201, "/reserve_ticket/ did not return status code 201 correctly. ")
        self.assertEqual(response.data, payment_pk)
#         self.assertIsNotNone(response.cookies.get("sessionid", None), "/reserve_ticket/ did not give a session cookie. ")

    def test_too_many_tickets(self):
        response = self.client.post(
            "/reserve_ticket/", 
            {
                "chapter_event": str(self.test_event.pk),
                "tickets": [
                    {
                        "ticket_type": self.test_ticket.pk,
                        "count": 9
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
    
    def test_out_of_tickets(self):
        prep_res = self.client.post(
            "/reserve_ticket/", 
            {
                "chapter_event": str(self.test_event.pk),
                "tickets": [
                    {
                        "ticket_type": self.test_ticket.pk,
                        "count": 5
                    }
                ]
            },
            content_type="application/json"
        )
       
        if prep_res.status_code != 201:
            raise Exception("Failed to perform reservation of tickets in preparation for testing test_expired_session_out_of_tickets.")

        self.client = Client()

        response = self.client.post(
            "/reserve_ticket/", 
            {
                "chapter_event": str(self.test_event.pk),
                "tickets": [
                    {
                        "ticket_type": self.test_ticket.pk,
                        "count": 6
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
        
    def test_negative_tickets(self):
        response = self.client.post(
            "/reserve_ticket/", 
            {
                "chapter_event": str(self.test_event.pk),
                "tickets": [
                    {
                        "ticket_type": self.test_ticket.pk,
                        "count": -1
                    },
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_zero_tickets(self):
        response = self.client.post(
            "/reserve_ticket/", 
            {
                "chapter_event": str(self.test_event.pk),
                "tickets": [
                    {
                        "ticket_type": self.test_ticket2.pk,
                        "count": 0
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_nonexisting_chapter_event(self):
        event_id: int = 9999 if self.test_event.pk != 9999 else 1
        response = self.client.post(
               "/reserve_ticket/", 
            {
                "chapter_event": event_id,
                "tickets": [
                    {
                        "ticket_type": self.test_ticket.pk,
                        "count": 1
                    },
                    {
                        "ticket_type": self.test_ticket2.pk,
                        "count": 1
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

    def test_double_reservation(self):
        r1 = self.client.post(
               "/reserve_ticket/", 
            {
                "chapter_event": self.test_event.pk,
                "tickets": [
                    {
                        "ticket_type": self.test_ticket.pk,
                        "count": 1
                    },
                    {
                        "ticket_type": self.test_ticket2.pk,
                        "count": 1
                    }
                ]
            },
            content_type="application/json"
        )
        if r1.status_code != 201:
            raise Exception("Failed to perform reservation of tickets in preparation for testing test_double_reservation.")

        # s1 = r1.cookies.get("sessionid")
        # p1_id = self.client.session["reserved_payment"]
        p1_id = r1.data

        r2 = self.client.post(
               "/reserve_ticket/", 
            {
                "chapter_event": self.test_event.pk,
                "session_id": p1_id,
                "tickets": [
                    {
                        "ticket_type": self.test_ticket.pk,
                        "count": 1
                    },
                    {
                        "ticket_type": self.test_ticket2.pk,
                        "count": 1
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(r2.status_code, 201)
        p1 = Payment.objects.get(pk=p1_id)
        # s2 = r2.cookies.get("sessionid")
        # p2_id = self.client.session["reserved_payment"]
        p2_id = r2.data
        p2 = Payment.objects.get(pk=p2_id)

        self.assertNotEqual(p1_id, p2_id, "/reserve_ticket/ did not replace the old session when double booking.")
        self.assertEqual(p1.status, PaymentStatus.FAILED_EXPIRED_RESERVATION)
        self.assertEqual(p2.status, PaymentStatus.RESERVED)

    def test_nonexisting_ticket_type(self):
        response = self.client.post(
               "/reserve_ticket/", 
            {
                "chapter_event": self.test_event.pk,
                "tickets": [
                    {
                        "ticket_type": max(self.test_ticket.pk, self.test_ticket2.pk, self.secret_ticket.pk) + 1,
                        "count": 1
                    },
                    {
                        "ticket_type": self.test_ticket2.pk,
                        "count": 1
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404, "/reserve_ticket did not return status 404 when reserving non-existent ticket. ")

        response = self.client.post(
               "/reserve_ticket/", 
            {
                "chapter_event": self.test_event.pk,
                "tickets": [
                    {
                        "ticket_type": self.secret_ticket.pk,
                        "count": 1
                    },
                    {
                        "ticket_type": self.test_ticket2.pk,
                        "count": 1
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404, "/reserve_ticket did not return status 404 when reserving secret ticket. ")

    def test_invalid_json_format(self):
        response = self.client.post(
               "/reserve_ticket/", 
            {
                "chapter_event": self.test_event.pk,
                "tickets": [
                    {
                        "ticket_type": self.test_ticket.pk,
                        "count": 1
                    },
                    {
                        "ticket_type": self.test_ticket2.pk,
                    }
                ]
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
