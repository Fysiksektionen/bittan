from django.db import models
from djmoney.models.fields import MoneyField
import datetime

class TicketType(models.Model):
	price = MoneyField(max_digits=19, decimal_places=2, default_currency='SEK')
	title = models.TextField()
	description = models.TextField()
	reservation_duration = models.DurationField(default=datetime.timedelta(hours=1))
	is_visible = models.BooleanField(default=True)
