from django.test import TestCase, Client
from rest_framework import status
from django.utils import timezone
import datetime
from bittan.models import ChapterEvent

class GetChaptereventsTest(TestCase):

	def setUp(self):
		pass

	def test_empty(self):
		c = Client()
		response = c.get("/get_chapterevents/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		data = response.json()
		self.assertEqual(data, [])
	
	def test_filled(self):
		now = timezone.now()
		ChapterEvent.objects.create(title="Title1", description="Description1", max_tickets=10, sales_stop_at=now+datetime.timedelta(days=365), event_at=now+datetime.timedelta(days=2))
		ChapterEvent.objects.create(title="Title2", description="Description2", max_tickets=10, sales_stop_at=now+datetime.timedelta(days=365), event_at=now+datetime.timedelta(days=1))
		c = Client()
		response = c.get("/get_chapterevents/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		data = response.json()
		self.assertEqual(len(data), 2)
		
		ce1 = data[0]
		self.assertEqual(ce1['title'], "Title2")
		self.assertEqual(ce1['description'], "Description2")
		self.assertEqual(type(ce1['event_at']), str) # We don't bother checking the exact content because it contains the datetime up to milliseconds

		ce2 = data[1]
		self.assertEqual(ce2['title'], "Title1")
		self.assertEqual(ce2['description'], "Description1")
		self.assertEqual(type(ce2['event_at']), str) # We don't bother checking the exact content because it contains the datetime up to milliseconds

	def test_sales_stop_at_past(self):
		now = timezone.now()
		ChapterEvent.objects.create(title="t", description="d", max_tickets=10, sales_stop_at=now+datetime.timedelta(days=365), event_at=now+datetime.timedelta(days=365))
		ChapterEvent.objects.create(title="t2", description="d2", max_tickets=10, sales_stop_at=now-datetime.timedelta(days=365), event_at=now-datetime.timedelta(days=365))
		c = Client()
		response = c.get("/get_chapterevents/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		data = response.json()
		self.assertEqual(len(data), 1)
		self.assertEqual(data[0]['title'], "t")
