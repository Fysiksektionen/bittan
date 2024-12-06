from django.db import models
from django.utils import timezone

class ChapterEvent(models.Model):
	title = models.TextField()
	description = models.TextField()
	total_seats = models.IntegerField()
	max_tickets_per_payment = models.IntegerField(default=8)
	sales_stop_at = models.DateTimeField()
	ticket_types = models.ManyToManyField('TicketType')
	reservation_duration = models.DurationField(default=timezone.timedelta(hours=1))
	event_at = models.DateTimeField()
