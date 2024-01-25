from django.db import models
from djmoney.models.fields import MoneyField
from djmoney.money import Money

class ChapterEvent(models.Model):
	title = models.TextField()
	description = models.TextField()
	max_tickets = models.IntegerField()
	sales_stop_at = models.DateTimeField()
	ticket_types = models.ManyToManyField('TicketType')

	@property
	def total_price(self) -> float:
		"""
		Returns the total price of all paid (non admin-generated) ticets. 
		"""
		return sum([x.price * x.ticket_set.filter(status="PAID").count() for x in self.ticket_types.all()])
