from bittan.models.payment import PaymentStatus, PaymentMethod
from unittest.mock import patch
from django.test import TestCase, Client


from datetime import datetime
from django.utils import timezone

from bittan.models import Answer, AnswerSelectedOptions, TicketType, ChapterEvent, Payment, Question, QuestionOption
from bittan.models.question import QuestionType
from bittan.services.swish.swish import Swish

class StartPaymentTest(TestCase):
    def setUp(self):
        NOW = timezone.now()
        self.test_event = ChapterEvent.objects.create(title="Test Event1", description="An event for testing. ", total_seats=10, sales_stop_at=NOW+timezone.timedelta(days=365), event_at=NOW+timezone.timedelta(days=366))
        
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
                "email_address": "mail@mail.com",
                "tickets": [
                    {
                        "ticket_type": self.test_ticket.pk,
                        "count": 4
                        }
                    ]
            },
            content_type="application/json"
        )
        self.session_id = self.reservation_response.data

        self.swish = Swish.get_instance()

    def test_start_payment(self):
        response = self.client.post(
            "/start_payment/",
            {
                "session_id": self.session_id
            }
        )

        self.assertEqual(response.status_code, 200)

        payment = Payment.objects.get(pk=self.session_id)
        swish_payment_request = self.swish.get_payment_request(payment.swish_id)

        self.assertEqual(payment.payment_started, True)
        self.assertEqual(payment.status, PaymentStatus.RESERVED)
        self.assertEqual(payment.payment_method, PaymentMethod.SWISH)
        self.assertEqual(swish_payment_request.amount, 4*self.test_ticket.price)

    def test_start_payment_non_fcfs_non_confirmed(self):
        self.test_event.fcfs = False
        self.test_event.save()
        response = self.client.post(
            "/start_payment/",
            {
                "session_id": self.session_id
            }
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, "PaymentNotPayable")

        payment = Payment.objects.get(pk=self.session_id)
        self.assertEqual(payment.payment_started, False)
        self.assertEqual(payment.status, PaymentStatus.RESERVED)

    def test_start_payment_non_fcfs_confirmed(self):
        self.test_event.fcfs = False
        self.test_event.save()
        payment = Payment.objects.get(pk=self.session_id)
        payment.status = PaymentStatus.CONFIRMED
        payment.save()
        response = self.client.post(
            "/start_payment/",
            {
                "session_id": self.session_id
            }
        )

        self.assertEqual(response.status_code, 200)

        payment = Payment.objects.get(pk=self.session_id)
        swish_payment_request = self.swish.get_payment_request(payment.swish_id)

        self.assertEqual(payment.payment_started, True)
        self.assertEqual(payment.status, PaymentStatus.CONFIRMED)
        self.assertEqual(payment.payment_method, PaymentMethod.SWISH)
        self.assertEqual(swish_payment_request.amount, 4*self.test_ticket.price)

    def test_start_payment_form_fcfs(self):
        q1 = Question.objects.create(
            title="Test question",
            question_type=QuestionType.RADIO,
            chapter_event=self.test_event
        )
        response = self.client.post(
            "/start_payment/",
            {
                "session_id": self.session_id
            }
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, "PaymentNotPayable")

        payment = Payment.objects.get(pk=self.session_id)
        self.assertEqual(payment.payment_started, False)
        self.assertEqual(payment.status, PaymentStatus.RESERVED)

        payment.status = PaymentStatus.FORM_SUBMITTED
        payment.save()
        response = self.client.post(
            "/start_payment/",
            {
                "session_id": self.session_id
            }
        )
        self.assertEqual(response.status_code, 200)

        payment = Payment.objects.get(pk=self.session_id)
        swish_payment_request = self.swish.get_payment_request(payment.swish_id)

        self.assertEqual(payment.payment_started, True)
        self.assertEqual(payment.status, PaymentStatus.FORM_SUBMITTED)
        self.assertEqual(payment.payment_method, PaymentMethod.SWISH)
        self.assertEqual(swish_payment_request.amount, 4*self.test_ticket.price)

    def test_start_payment_form_non_fcfs(self):
        q1 = Question.objects.create(
            title="Test question",
            question_type=QuestionType.RADIO,
            chapter_event=self.test_event
        )
        self.test_event.fcfs = False
        self.test_event.save()
        response = self.client.post(
            "/start_payment/",
            {
                "session_id": self.session_id
            }
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, "PaymentNotPayable")

        payment = Payment.objects.get(pk=self.session_id)
        self.assertEqual(payment.payment_started, False)
        self.assertEqual(payment.status, PaymentStatus.RESERVED)

        payment.status = PaymentStatus.FORM_SUBMITTED
        payment.save()
        response = self.client.post(
            "/start_payment/",
            {
                "session_id": self.session_id
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, "PaymentNotPayable")

        payment = Payment.objects.get(pk=self.session_id)
        self.assertEqual(payment.payment_started, False)
        self.assertEqual(payment.status, PaymentStatus.FORM_SUBMITTED)

        payment.status = PaymentStatus.CONFIRMED
        payment.save()
        response = self.client.post(
            "/start_payment/",
            {
                "session_id": self.session_id
            }
        )
        self.assertEqual(response.status_code, 200)

        payment = Payment.objects.get(pk=self.session_id)
        swish_payment_request = self.swish.get_payment_request(payment.swish_id)

        self.assertEqual(payment.payment_started, True)
        self.assertEqual(payment.status, PaymentStatus.CONFIRMED)
        self.assertEqual(payment.payment_method, PaymentMethod.SWISH)
        self.assertEqual(swish_payment_request.amount, 4*self.test_ticket.price)

    
    def test_no_session_id(self):
        response = self.client.post(
            "/start_payment/",
            {
                "email_address": "mail@mail.com",
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_non_existent_session_id(self):
        response = self.client.post(
            "/start_payment/",
            {
                "email_address": "mail@mail.com",
                "session_id": "Existerar ej"
            }
        )
        self.assertEqual(response.status_code, 404)

    def test_expired_session_out_of_tickets(self):
        payment = Payment.objects.get(pk=self.session_id)
        payment.status = PaymentStatus.FAILED_EXPIRED_RESERVATION
        payment.save()

        client2 = Client()
        prep_res = client2.post(
            "/reserve_ticket/", 
            {
                "chapter_event": str(self.test_event.pk),
                "email_address": "mail@mail.com",
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
                "session_id": self.session_id
            }
        )
        self.assertEqual(response.status_code, 408) 

        payment = Payment.objects.get(pk=self.session_id)
        self.assertEqual(payment.status, PaymentStatus.FAILED_EXPIRED_RESERVATION)
        self.assertEqual(payment.payment_started, False)

    @patch('django.utils.timezone.now')
    def test_expired_session_rebook_tickets(self, mock_now):
        now = datetime(1970, 1, 1, tzinfo=timezone.timezone.utc)
        mock_now.return_value = now

        payment = Payment.objects.get(pk=self.session_id)
        payment.status = PaymentStatus.FAILED_EXPIRED_RESERVATION
        payment.save()

        mail_address = "mail@mail.com"
        response = self.client.post(
            "/start_payment/",
            {
                "session_id": self.session_id
            }
        )

        self.assertEqual(response.status_code, 200)

        payment = Payment.objects.get(pk=self.session_id)
        swish_payment_request = self.swish.get_payment_request(payment.swish_id)

        self.assertEqual(payment.payment_started, True)
        self.assertEqual(payment.email, mail_address)
        self.assertEqual(payment.status, PaymentStatus.RESERVED)
        self.assertEqual(payment.expires_at, now + self.test_event.reservation_duration)
        self.assertEqual(payment.payment_method, PaymentMethod.SWISH)
        self.assertEqual(swish_payment_request.amount, 4*self.test_ticket.price)

    def test_already_paid_payment(self):
        mail_address = "mail@mail.com"

        payment = Payment.objects.get(pk=self.session_id)
        payment.status = PaymentStatus.PAID
        payment.save()

        response = self.client.post(
            "/start_payment/",
            {
                "session_id": self.session_id
            }
        )

        self.assertEqual(response.status_code, 403)

    def test_form_payment(self):
        q1 = Question.objects.create(
            title = "Alkohol", 
            question_type = QuestionType.MULTIPLE_CHOICE,
            chapter_event = self.test_event
        ) 
        q1_opt1 = QuestionOption.objects.create(
            price = 100,
            name = "Mycket",
            has_text = False,
            question=q1
        )
        q1_opt2 = QuestionOption.objects.create(
            price = 0,
            name = "Inget",
            has_text = False,
            question=q1
        )
        payment = Payment.objects.get(id=self.session_id)
        ticket = payment.ticket_set.first()
        answer = Answer.objects.create(
            question = q1,
            ticket=ticket
        )
        _ = AnswerSelectedOptions.objects.create(
            question_option = q1_opt1,
            answer = answer,
        )
        _ = AnswerSelectedOptions.objects.create(
            question_option = q1_opt2,
            answer = answer,
        )
        payment.status = PaymentStatus.FORM_SUBMITTED
        payment.save()
        response = self.client.post(
            "/start_payment/",
            {
                "session_id": self.session_id
            }
        )

        self.assertEqual(response.status_code, 200)

        payment = Payment.objects.get(pk=self.session_id)
        swish_payment_request = self.swish.get_payment_request(payment.swish_id)

        self.assertEqual(payment.payment_started, True)
        self.assertEqual(payment.status, PaymentStatus.FORM_SUBMITTED)
        self.assertEqual(payment.payment_method, PaymentMethod.SWISH)
        self.assertEqual(swish_payment_request.amount, 4*self.test_ticket.price + q1_opt1.price + q1_opt2.price)


