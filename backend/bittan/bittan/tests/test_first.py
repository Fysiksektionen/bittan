from django.test import TestCase
from bittan.models import TicketType

class FirstTestCase(TestCase):

	def setUp(self):
		pass

	def test_sample(self):
		t = TicketType.objects.create(price=0.99, title="My Title", description="My description")
		self.assertEqual(t.title, "My Title")
		self.assertNotEqual(t.title, "Not My Title")
