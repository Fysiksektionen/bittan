from django.db import models

class AnswerSelectedOptions(models.Model):
    question_option = models.ForeignKey("QuestionOption", on_delete=models.DO_NOTHING)
    anwser = models.ForeignKey("Answer", on_delete=models.DO_NOTHING)
    text = models.TextField(default="")

