from django.test import TestCase, Client
from rest_framework import status
from django.utils import timezone
import datetime
from bittan.models import ChapterEvent, TicketType, Question, QuestionType, QuestionOption

class GetChapterEventTest(TestCase):
	
	QUESTIONS = [
		{
			"title": "Namn",
			"description": "Desc1",
			"question_type": QuestionType.RADIO,
			"options": [
				{"name": "Namn", "description": "", "price": 0, "has_text": True}
			],
		}, 
		{
			"title": "Speckost",
			"description": "Desc2",
			"question_type": QuestionType.MULTIPLE_CHOICE,
			"options": [
				{"name": "Gluten", "description": "", "price": 0, "has_text": False},
				{"name": "Laktos", "description": "", "price": 0, "has_text": False},
				{"name": "Övrigt", "description": "", "price": 0, "has_text": True},
			],
		},
		{
			"title": "Alk?",
			"description": "Alkohol",
			"question_type": QuestionType.RADIO,
			"options": [
				{"name": "Ja", "description": "1 punsch + 1 nubbe", "price": 100, "has_text": False},
				{"name": "Nej", "description": "Ingen alk", "price": 0, "has_text": False},
			],
		},
	]

	def setUp(self):
		self.Client=Client()
		now = timezone.now()
		self.ticket_type1 = TicketType.objects.create(title="ticket_type1", description="tt1", price=10)
		self.hidden_ticket_type = TicketType.objects.create(title="Hidden ticket type", description="htt", price=0, is_visible=False)

		self.ce = ChapterEvent.objects.create(
			title="title1", 
			description="Desc1",
			total_seats=10,
			sales_stop_at=now+datetime.timedelta(days=365),
			event_at=now+datetime.timedelta(days=1)
		)
		
		self.ce.ticket_types.add(self.ticket_type1, self.hidden_ticket_type)

		self.questions = []
		self.question_options = {}

		for question_data in self.QUESTIONS:
			question = Question.objects.create(
				title=question_data["title"],
				description=question_data["description"],
				question_type=question_data["question_type"],
				chapter_event=self.ce
			) 

			options = []
			for option_data in question_data["options"]:
				option = QuestionOption.objects.create(
					name=option_data["name"],
					description=option_data["description"],
					price=option_data["price"],
					has_text=option_data["has_text"],
					question=question
				)
				options.append(option)

			self.question_options[question.pk] = options
			self.questions.append(question)



	def test_non_existent_ce(self):
		res = self.client.get(f"/get_chapterevents/{self.ce.pk+1}")
		self.assertEqual(res.status_code, 404)
	
	def test_filled_form(self):
		res = self.client.get(f"/get_chapterevents/{self.ce.pk}")
		self.assertEqual(res.status_code, 200)

		data = res.json()

		res_ce = data["chapter_event"]
		self.assertEqual(res_ce['title'], self.ce.title)
		self.assertEqual(res_ce['description'], self.ce.description)
		self.assertEqual(res_ce['max_tickets_per_payment'], self.ce.max_tickets_per_payment)
		self.assertEqual(res_ce['tickets_left'], self.ce.total_seats - self.ce.alive_ticket_count)
		self.assertEqual(type(res_ce['event_at']), str) # We don't bother checking the exact content because it contains the datetime up to milliseconds
		self.assertEqual(type(res_ce['sales_stop_at']), str) # We don't bother checking the exact content because it contains the datetime up to milliseconds
		self.assertEqual(res_ce['ticket_types'], [ticket_type.pk for ticket_type in self.ce.ticket_types.all()])

		questions_res = sorted(data["questions"], key=lambda q: q["id"])
		questions_exp = sorted(self.questions, key=lambda q: q.pk)

		self.assertEqual(len(questions_exp), len(questions_res))

		for q_exp, q_res in zip(questions_exp, questions_res):
			self.assertEqual(q_exp.pk, q_res["id"])
			self.assertEqual(q_exp.title, q_res['title'])
			self.assertEqual(q_exp.description, q_res['description'])
			self.assertEqual(q_exp.question_type, q_res['question_type'])
			self.assertEqual(q_exp.questionoption_set.count(), len(q_res['options']))

			opts_res = sorted(q_res["options"], key=lambda o: o["id"])
			opts_exp = sorted(q_exp.questionoption_set.all(), key=lambda o: o.id)

			for o_exp, o_res in zip(opts_exp, opts_res):
				self.assertEqual(o_exp.name, o_res['name'])
				self.assertEqual(o_exp.description, o_res['description'])
				self.assertEqual(o_exp.price, o_res['price'])
				self.assertEqual(o_exp.has_text, o_res['has_text'])
			
