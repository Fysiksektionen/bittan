from django.db import models
from djmoney.models.fields import MoneyField
import datetime

class TicketStatus(models.TextChoices):
	PAID = "PAID"
	FAILED_BY_ADMIN = "FAILED_BY_ADMIN"
	ALIVE = "ALIVE"

class Ticket(models.Model):
	external_id = models.TextField()
	time_created = models.DateTimeField()
	payment = models.ForeignKey('Payment', on_delete=models.DO_NOTHING)
	status = models.TextField(choices=TicketStatus)
	ticket_type = models.ForeignKey('TicketType', on_delete=models.DO_NOTHING)
