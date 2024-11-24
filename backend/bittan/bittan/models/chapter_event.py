from django.db import models
from django.utils import timezone

from bittan.models.payment import PaymentStatus

class ChapterEvent(models.Model):
	title = models.TextField()
	description = models.TextField()
	max_tickets = models.IntegerField()
	sales_stop_at = models.DateTimeField()
	ticket_types = models.ManyToManyField('TicketType')
	reservation_duration = models.DurationField(default=timezone.timedelta(hours=1))
	swish_message = models.TextField(max_length=50)

	def save(self, *args, **kwargs):
		if not self.swish_message:
			self.swish_message = self.title[:50]
		super(ChapterEvent, self).save(*args, **kwargs)

	@property
	def alive_ticket_count(self) -> int:
		"""
		Returns the total count of alive tickets for the chapter event. 
		"""
		ticket_types = self.ticket_types.all()
		
		count = 0
		for ticket_type in ticket_types:
			count += ticket_type.ticket_set.filter(payment__status__in=[PaymentStatus.PAID, PaymentStatus.RESERVED]).count()				
		return count
	event_at = models.DateTimeField()
