from django.db import models
from djmoney.models.fields import MoneyField
import datetime

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
	