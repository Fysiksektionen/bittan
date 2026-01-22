from django.db import models


class AnswerSelectedOptions(models.Model):
    question_option = models.ForeignKey("QuestionOption", related_name="answer_selected_options", on_delete=models.DO_NOTHING)
    answer = models.ForeignKey("Answer", on_delete=models.DO_NOTHING)
    text = models.TextField(null=True)
