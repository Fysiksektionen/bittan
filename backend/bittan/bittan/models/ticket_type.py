from django.db import models

class TicketType(models.Model):
	price = models.IntegerField()
	title = models.TextField()
	description = models.TextField()
	is_visible = models.BooleanField(default=True)
