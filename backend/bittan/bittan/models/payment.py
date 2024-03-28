from django.db import models

class PaymentStatus(models.TextChoices):
	RESERVED = "RESERVED"
	PAID = "PAID"
	FAILED_EXPIRED_RESERVATION = "FAILED_EXPIRED_RESERVATION"
	FAILED_ADMIN = "FAILED_ADMIN"

class Payment(models.Model):
	expires_at = models.DateTimeField()
	swish_id = models.TextField()
	status = models.TextField(choices=PaymentStatus)
	email = models.TextField()
	sent_email = models.BooleanField(default=False)
	payment_started = models.BooleanField(default=False)
