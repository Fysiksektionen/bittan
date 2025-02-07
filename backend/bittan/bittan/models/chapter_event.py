from django.db import models
from django.utils import timezone

from bittan.models.payment import PaymentStatus

class ChapterEvent(models.Model):
	title = models.TextField()
	description = models.TextField()
	total_seats = models.IntegerField()
	max_tickets_per_payment = models.IntegerField(default=8)
	sales_stop_at = models.DateTimeField()
	ticket_types = models.ManyToManyField('TicketType')
	reservation_duration = models.DurationField(default=timezone.timedelta(hours=1))
	swish_message = models.TextField(max_length=50)
	event_at = models.DateTimeField()
	door_open_before = models.DurationField(default=timezone.timedelta(hours=1))

	def save(self, *args, **kwargs):
		if not self.swish_message:
			self.swish_message = self.title[:50]
		super(ChapterEvent, self).save(*args, **kwargs)

	@property
	def alive_ticket_count(self) -> int:
		"""
		Returns the total count of alive tickets for the chapter event. 
		"""
		count = self.ticket_set.prefetch_related("payment").filter(payment__status__in=[PaymentStatus.PAID, PaymentStatus.RESERVED]).count()
		return count

	def __str__(self):
		return self.title
