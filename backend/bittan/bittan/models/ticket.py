from django.db import models
import random


def generate_ticket_external_id():
    return "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(6))


class Ticket(models.Model):
    external_id = models.TextField(unique=True, default=generate_ticket_external_id)
    time_created = models.DateTimeField()
    payment = models.ForeignKey("Payment", on_delete=models.DO_NOTHING)
    ticket_type = models.ForeignKey("TicketType", on_delete=models.DO_NOTHING)
    times_used = models.IntegerField(default=0)
    chapter_event = models.ForeignKey("ChapterEvent", on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return self.external_id
