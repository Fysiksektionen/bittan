from django.db import models

class Answer(models.Model):
    question = models.ForeignKey("Question", on_delete=models.DO_NOTHING)
    ticket = models.ForeignKey("Ticket", on_delete=models.DO_NOTHING)
