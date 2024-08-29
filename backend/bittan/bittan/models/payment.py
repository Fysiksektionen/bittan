from django.db import models
from django.db.models import Q
import operator
from functools import reduce

from django.db.models import F, Case, When, Value

class PaymentStatus(models.TextChoices):
	RESERVED = "RESERVED"
	PAID = "PAID"
	FAILED_EXPIRED_RESERVATION = "FAILED_EXPIRED_RESERVATION"
	FAILED_ADMIN = "FAILED_ADMIN"

	@staticmethod
	def get_failed_query():
		failed_statuses = [
			PaymentStatus.FAILED_ADMIN, 
			PaymentStatus.FAILED_EXPIRED_RESERVATION
		]
		return reduce(operator.or_, [Q(status=stat) for stat in failed_statuses])


	

class Payment(models.Model):
	expires_at = models.DateTimeField()
	swish_id = models.TextField(null=True, blank=True)
	status = models.TextField(choices=PaymentStatus)
	email = models.TextField(null=True, blank=True)
	sent_email = models.BooleanField(default=False)
	payment_started = models.BooleanField(default=False)