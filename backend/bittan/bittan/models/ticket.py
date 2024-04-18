from django.db import models

class Ticket(models.Model):
	external_id = models.TextField()
	# time_created = models.DateTimeField(default=datetime.datetime.now())
	payment = models.ForeignKey('Payment', on_delete=models.DO_NOTHING)
	ticket_type = models.ForeignKey('TicketType', on_delete=models.DO_NOTHING)
