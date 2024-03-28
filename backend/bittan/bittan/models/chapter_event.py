from django.db import models
import datetime

class ChapterEvent(models.Model):
	title = models.TextField()
	description = models.TextField()
	max_tickets = models.IntegerField()
	sales_stop_at = models.DateTimeField()
	ticket_types = models.ManyToManyField('TicketType')
	reservation_duration = models.DurationField(default=datetime.timedelta(hours=1))
