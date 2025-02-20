from django.db import models

class PaymentStatus(models.TextChoices):
	RESERVED = "RESERVED"
	PAID = "PAID"
	FAILED_EXPIRED_RESERVATION = "FAILED_EXPIRED_RESERVATION"
	FAILED_ADMIN = "FAILED_ADMIN"

class PaymentMethod(models.TextChoices):
	SWISH = "SWISH"
	ADMIN_GENERATED = "ADMIN_GENERATED"

class Payment(models.Model):
	expires_at = models.DateTimeField()
	swish_id = models.TextField(null=True, blank=True)
	status = models.TextField(choices=PaymentStatus)
	email = models.TextField(null=True, blank=True)
	sent_email = models.BooleanField(default=False)
	payment_started = models.BooleanField(default=False)
	payment_method = models.TextField(choices=PaymentMethod, null=True, blank=True)
