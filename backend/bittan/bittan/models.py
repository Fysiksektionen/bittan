from django.db import models
from djmoney.models.fields import MoneyField
import datetime

class TicketType(models.Model):
	price = MoneyField(max_digits=19, decimal_places=2, default_currency='SEK')
	title = models.TextField()
	description = models.TextField()
	reservation_duration = models.DurationField(default=datetime.timedelta(hours=1))

class ChapterEvent(models.Model):
	title = models.TextField()
	description = models.TextField()
	max_tickets = models.IntegerField()
	sales_stop_at = models.DateTimeField()
	ticket_types = models.ManyToManyField(TicketType)

class PaymentStatus(models.TextChoices):
	ALIVE = "ALIVE"
	FAILED_EXPIRED_RESERVATION = "FAILED_EXPIRED_RESERVATION"
	FAILED_BY_ADMIN = "FAILED_BY_ADMIN"

class Payment(models.Model):
	time_created = models.DateTimeField()
	swish_id = models.TextField()
	status = models.TextField(choices=PaymentStatus)
	telephone_number = models.TextField()
	email = models.TextField()
	total_price = MoneyField(max_digits=19, decimal_places=2, default_currency='SEK')
	sent_email = models.BooleanField(default=False)

class TicketStatus(models.TextChoices):
	PAID = "PAID"
	FAILED_BY_ADMIN = "FAILED_BY_ADMIN"

class Ticket(models.Model):
	external_id = models.TextField()
	time_created = models.DateTimeField()
	payment = models.ForeignKey(Payment, on_delete=models.DO_NOTHING)
	status = models.TextField(choices=TicketStatus)
	ticket_type = models.ForeignKey(TicketType, on_delete=models.DO_NOTHING)
