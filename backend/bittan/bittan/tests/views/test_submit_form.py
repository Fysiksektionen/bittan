from bittan.models.payment import PaymentStatus
from django.test import TestCase, Client
from django.utils import timezone
from django.db.models import Max

from bittan.models import Answer, AnswerSelectedOptions, ChapterEvent, Payment, Ticket, TicketType, Question, QuestionOption
from bittan.models.question import QuestionType

class SubmitFormTest(TestCase):

	QUESTIONS = [
			{
				"title": "Mandatory textbox",
				"description": "Desc1",
				"question_type": QuestionType.RADIO,
				"options": [
					{"name": "Namn", "description": "", "price": 0, "text": True}
				],
			}, 
			{
				"title": "Optional textbox",
				"description": "",
				"question_type": QuestionType.MULTIPLE_CHOICE,
				"options": [
					{"name": "Övrigt", "description": "", "price": 0, "text": True}
				]
			},
			{
				"title": "Multiple choice",
				"description": "Desc2",
				"question_type": QuestionType.MULTIPLE_CHOICE,
				"options": [
					{"name": "Gluten", "description": "", "price": 0, "text": False},
					{"name": "Laktos", "description": "", "price": 0, "text": False},
					{"name": "Övrigt", "description": "", "price": 0, "text": True},
				],
			},
			{
				"title": "Radio",
				"description": "Desc2",
				"question_type": QuestionType.RADIO,
				"options": [
					{"name": "Gött", "description": "", "price": 0, "text": False},
					{"name": "Nött", "description": "", "price": 0, "text": False},
					{"name": "Annat", "description": "", "price": 0, "text": True},
				],
			},
			{
				"title": "Mandatory checkbox", # (one choice radio)
				"description": "Uppförandepolicy",
				"question_type": QuestionType.RADIO,
				"options": [
					{"name": "Ja", "description": "", "price": 0, "text": False},
				],
			},
			{
				"title": "Optional checkbox", # (one choice multiple choice)
				"description": "",
				"question_type": QuestionType.MULTIPLE_CHOICE,
				"options": [
					{"name": "Ja", "description": "", "price": 0, "text": False},
				],
			}
	]

	def setUp(self):
		NOW = timezone.now()
		self.test_event = ChapterEvent.objects.create(
				title="Test Event", 
				description="An event for testing. ", 
				total_seats=10, 
				max_tickets_per_payment = 8,
				sales_stop_at=NOW+timezone.timedelta(days=365), 
				event_at=NOW+timezone.timedelta(days=366),
				fcfs=True
				)
		self.test_ticket = TicketType.objects.create(price=200, title="Test Ticket", description="A ticket for testing.")
		self.test_event.ticket_types.add(self.test_ticket)

		self.client = Client()

		self.session_id = self.client.post(
            "/reserve_ticket/", 
            {
                "chapter_event": str(self.test_event.pk),
                "email_address": "mail@mail.com",
                "tickets": [
                    {
                        "ticket_type": self.test_ticket.pk,
                        "count": 1
                    }
                ]
            },
            content_type="application/json"
        ).data
		self.questions = []
		self.question_options = {}

		for question_data in self.QUESTIONS:
			question = Question.objects.create(
					title=question_data["title"],
					description=question_data["description"],
					question_type=question_data["question_type"],
					chapter_event=self.test_event
					) 

			options = []
			for option_data in question_data["options"]:
				option = QuestionOption.objects.create(
						name=option_data["name"],
						description=option_data["description"],
						price=option_data["price"],
						has_text=option_data["text"],
						question=question
						)
				options.append(option)

			self.question_options[question.pk] = options
			self.questions.append(question)

	def generateFormSubmission(self):
		''' 
			Generates a correct submit form data dictionary. Submits "Some text" to all textboxes and chooses 
			first and last of checkboxes. 
		'''
		form_submission = {}
		for question in self.questions:
			question_obj = {"question_id": question.pk}
			opts = question.questionoption_set.all()
			if question.question_type == QuestionType.MULTIPLE_CHOICE:
				question_obj["option_ids"] = [opts.first().pk]
				question_obj["option_texts"] = ["Some text" if opts.first().has_text==True else ""]
				if opts.count() > 1:
					question_obj["option_ids"].append(opts.last().pk)
					question_obj["option_texts"].append("Some text" if opts.last().has_text==True else "")
			elif question.question_type == QuestionType.RADIO: # Set
				question_obj["option_ids"] = [opts.first().pk]
				question_obj["option_texts"] = ["Some text" if opts.first().has_text == True else ""]

			form_submission[question.pk] = question_obj
		return form_submission

	def test_correct_form(self):
		form_submission = self.generateFormSubmission()
		r = self.client.post(
			f"/submit_form/",
			{
				"session_id": self.session_id,
				"form_data": list(form_submission.values()),
			},
            content_type="application/json"
		)

		self.assertEqual(r.status_code, 200)

		ticket = Ticket.objects.get(payment_id=self.session_id)

		for question in form_submission.values():
			answer_db = Answer.objects.filter(
				ticket=ticket,
				question__pk = question["question_id"]
			)
			self.assertEqual(answer_db.count(), 1)
			answer_options_db = AnswerSelectedOptions.objects.filter(answer=answer_db.first())
			self.assertEqual(answer_options_db.count(), len(question["option_ids"]))

			for option_correct_id, option_correct_text in zip(question["option_ids"], question["option_texts"]):
				answer_option_db = answer_options_db.get(question_option__pk=option_correct_id)
				self.assertEqual(answer_option_db.text, option_correct_text) 

		p = Payment.objects.get(id=self.session_id)
		self.assertEqual(p.status, PaymentStatus.FORM_SUBMITTED)

	def test_radio_too_many_options(self):
		form_submission = self.generateFormSubmission()
		q = Question.objects.get(title="Radio")
		
		form_submission[q.pk] = {
			"question_id": q.pk,
			"option_ids": list(q.questionoption_set.values_list("id", flat=True)),
			"option_texts": [""]*q.questionoption_set.count()
		} 

		r = self.client.post(
			f"/submit_form/",
			{
				"session_id": self.session_id,
				"form_data": list(form_submission.values()),
			},
            content_type="application/json"
		)

		self.assertEqual(r.status_code, 400)
		self.assertEqual(r.data, "TooManyOptions")
		p = Payment.objects.get(id=self.session_id)
		self.assertEqual(p.status, PaymentStatus.RESERVED)

	def test_radio_empty_answer(self):
		form_submission = self.generateFormSubmission()
		qpk = Question.objects.get(title="Radio").pk
		form_submission[qpk] = {"question_id": qpk, "option_ids": [], "option_texts": []} 

		r = self.client.post(
			f"/submit_form/",
			{
				"session_id": self.session_id,
				"form_data": list(form_submission.values()),
			},
            content_type="application/json"
		)

		self.assertEqual(r.status_code, 400)
		self.assertEqual(r.data, "UnansweredMandatory")
		p = Payment.objects.get(id=self.session_id)
		self.assertEqual(p.status, PaymentStatus.RESERVED)
		

	def test_radio_missing_answer(self):
		form_submission = self.generateFormSubmission()
		qpk = Question.objects.get(title="Radio").pk
		del form_submission[qpk]
		r = self.client.post(
			f"/submit_form/",
			{
				"session_id": self.session_id,
				"form_data": list(form_submission.values()),
			},
            content_type="application/json"
		)

		self.assertEqual(r.status_code, 400)
		self.assertEqual(r.data, "UnansweredMandatory")
		p = Payment.objects.get(id=self.session_id)
		self.assertEqual(p.status, PaymentStatus.RESERVED)
	
	def test_text_box_no_text_radio(self):
		form_submission = self.generateFormSubmission()
		q = Question.objects.get(title="Mandatory textbox")
		form_submission[q.pk] = {"question_id": q.pk, "option_ids": [q.questionoption_set.first().pk], "option_texts": [""]} 

		r = self.client.post(
			f"/submit_form/",
			{
				"session_id": self.session_id,
				"form_data": list(form_submission.values()),
			},
            content_type="application/json"
		)

		self.assertEqual(r.status_code, 400)
		self.assertEqual(r.data, "UnansweredMandatory")
		p = Payment.objects.get(id=self.session_id)
		self.assertEqual(p.status, PaymentStatus.RESERVED)

		form_submission = self.generateFormSubmission()
		q = Question.objects.get(title="Radio")
		form_submission[q.pk] = {"question_id": q.pk, "option_ids": [q.questionoption_set.get(name="Annat").pk], "option_texts": [""]} 

		r = self.client.post(
			f"/submit_form/",
			{
				"session_id": self.session_id,
				"form_data": list(form_submission.values()),
			},
            content_type="application/json"
		)

		self.assertEqual(r.status_code, 400)
		self.assertEqual(r.data, "UnansweredMandatory")
		p = Payment.objects.get(id=self.session_id)
		self.assertEqual(p.status, PaymentStatus.RESERVED)

		pass

	def test_non_existing_question(self):
		form_submission = {
				'session_id': self.session_id, 
				'form_data': [
					{
						'question_id': Question.objects.aggregate(Max("pk"))["pk__max"] + 1, 
						'option_ids': [1], 
						'option_texts': ['Some text']
					}, 
				]
		}
		r = self.client.post(
			f"/submit_form/",
			form_submission,
			content_type="application/json"
		)

		self.assertEqual(r.status_code, 404)
		self.assertEqual(r.data, "QuestionNotFound")
		p = Payment.objects.get(id=self.session_id)
		self.assertEqual(p.status, PaymentStatus.RESERVED)

	def test_non_existing_question_option(self):
		form_submission = {
				'session_id': self.session_id, 
				'form_data': [
					{
						'question_id': Question.objects.first().pk, 
						'option_ids': [QuestionOption.objects.aggregate(Max("pk"))["pk__max"] + 1], 
						'option_texts': ['Some text']
					}, 
				]
		}
		r = self.client.post(
			f"/submit_form/",
			form_submission,
			content_type="application/json"
		)

		self.assertEqual(r.status_code, 404)
		self.assertEqual(r.data, "QuestionOptionNotFound")
		p = Payment.objects.get(id=self.session_id)
		self.assertEqual(p.status, PaymentStatus.RESERVED)


	def test_expired_session(self):
		form_submission = self.generateFormSubmission()
		p = Payment.objects.get(id=self.session_id)
		p.status = PaymentStatus.FAILED_EXPIRED_RESERVATION
		p.save()
		r = self.client.post(
			f"/submit_form/",
			{
				"session_id": self.session_id,
				"form_data": list(form_submission.values()),
			},
            content_type="application/json"
		)
		self.assertEqual(r.status_code, 403)
		self.assertEqual(r.data, "SessionExpired")
		self.assertEqual(p.status, PaymentStatus.FAILED_EXPIRED_RESERVATION)


	def test_invalid_session(self):
		form_submission = self.generateFormSubmission()
		r = self.client.post(
			f"/submit_form/",
			{
				"session_id": 'a'*12 if self.session_id != 'a'*12 else 'b*12',
				"form_data": list(form_submission.values()),
			},
			content_type="application/json"
		)
		self.assertEqual(r.status_code, 404)
		self.assertEqual(r.data, "NoSessionFound")

