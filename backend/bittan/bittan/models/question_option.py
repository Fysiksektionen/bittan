from django.db import models

class QuestionOption(models.Model):
    name = models.TextField()
    description = models.TextField(default="")
    price = models.IntegerField()
    question = models.ForeignKey("Question", on_delete=models.DO_NOTHING)
    has_text = models.BooleanField()



