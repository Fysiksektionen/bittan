from django.db import models
from django.utils import timezone

class ChapterEvent(models.Model):
	title = models.TextField()
	description = models.TextField()
	max_tickets = models.IntegerField()
	sales_stop_at = models.DateTimeField()
	ticket_types = models.ManyToManyField('TicketType')
	reservation_duration = models.DurationField(default=timezone.timedelta(hours=1))

	@property
	def ticket_count(self) -> int:
		"""
		Returns the total count of alive tickets for the chapter event. 
		"""
		return sum(x.ticket_set.filter(status="ALIVE").count() for x in self.ticket_types.all())

	@property
	def total_price(self) -> float:
		"""
		Returns the total price of all paid (non admin-generated) ticets. 
		"""
		return sum(x.price * x.ticket_set.filter(status="PAID").count() for x in self.ticket_types.all())
	
	def total_price_by_ticket_type(self, ticket_type_id) -> float:
		return sum(x.price * x.ticket_set.filter(status="PAID").count() for x in self.ticket_types.filter(id=ticket_type_id))
	
