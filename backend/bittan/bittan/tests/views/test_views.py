from django.test import TestCase, Client
from rest_framework import status
from django.utils import timezone
import datetime
from bittan.models import ChapterEvent, TicketType

class GetChaptereventsTest(TestCase):

	def setUp(self):
		self.ticket_type1 = TicketType.objects.create(title="ticket_type1", description="tt1", price=10)
		self.ticket_type2 = TicketType.objects.create(title="ticket_type2", description="tt2", price=20)
		self.ticket_type3 = TicketType.objects.create(title="ticket_type3", description="tt3", price=30)

	def test_empty(self):
		c = Client()
		response = c.get("/get_chapterevents/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		data = response.json()
		self.assertEqual(data, {"chapter_events": [], "ticket_types": []})
	
	def test_filled(self):
		now = timezone.now()
		ce1_database = ChapterEvent.objects.create(title="Title1", description="Description1", total_seats=10, sales_stop_at=now+datetime.timedelta(days=365), event_at=now+datetime.timedelta(days=2))
		ce1_database.ticket_types.add(self.ticket_type1)
		ce2_database = ChapterEvent.objects.create(title="Title2", description="Description2", total_seats=10, sales_stop_at=now+datetime.timedelta(days=365), event_at=now+datetime.timedelta(days=1))
		ce2_database.ticket_types.add(self.ticket_type1, self.ticket_type2)
		ce_dbs = [ce1_database, ce2_database]
		c = Client()
		response = c.get("/get_chapterevents/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		data = response.json()

		chapter_events = data["chapter_events"]
		self.assertEqual(len(chapter_events), 2)
		for ce in chapter_events:
			for ce_db in ce_dbs:
				if ce["id"] == ce_db.id:
					corresponding_ce_db = ce_db
					break
			else:
				raise Exception("No corresponding chapter_event found")
			self.assertEqual(ce['title'], corresponding_ce_db.title)
			self.assertEqual(ce['description'], corresponding_ce_db.description)
			self.assertEqual(ce['max_tickets_per_payment'], corresponding_ce_db.max_tickets_per_payment)
			self.assertEqual(type(ce['event_at']), str) # We don't bother checking the exact content because it contains the datetime up to milliseconds
			self.assertEqual(type(ce['sales_stop_at']), str) # We don't bother checking the exact content because it contains the datetime up to milliseconds
			self.assertEqual(ce['ticket_types'], [ticket_type.id for ticket_type in corresponding_ce_db.ticket_types.all()])

		ticket_types = data["ticket_types"]
		ticket_types_db = [self.ticket_type1, self.ticket_type2]
		self.assertEqual(len(ticket_types), 2)
		for tt in ticket_types:
			for tt_db in ticket_types_db:
				if tt["id"] == tt_db.id:
					corresponding_tt_db = tt_db
					break
			else:
				raise Exception("No corresponding ticket_type found")
			self.assertEqual(tt['title'], corresponding_tt_db.title)
			self.assertEqual(tt['description'], corresponding_tt_db.description)
			self.assertEqual(tt['price'], corresponding_tt_db.price) 

	def test_sales_stop_at_past(self):
		now = timezone.now()
		ChapterEvent.objects.create(title="t", description="d", total_seats=10, sales_stop_at=now+datetime.timedelta(days=365), event_at=now+datetime.timedelta(days=365))
		ChapterEvent.objects.create(title="t2", description="d2", total_seats=10, sales_stop_at=now-datetime.timedelta(days=365), event_at=now-datetime.timedelta(days=365))
		c = Client()
		response = c.get("/get_chapterevents/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		data = response.json()
		chapter_events = data["chapter_events"]
		ticket_types = data["ticket_types"]
		self.assertEqual(len(chapter_events), 1)
		self.assertEqual(chapter_events[0]["title"], "t")
