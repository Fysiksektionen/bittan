from django.db import models

class Answer(models.Model):
    question = models.ForeignKey("Question", related_name="answers", on_delete=models.DO_NOTHING)
    ticket = models.ForeignKey("Ticket", on_delete=models.DO_NOTHING)
