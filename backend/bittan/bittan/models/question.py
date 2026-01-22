from django.db import models

class QuestionType(models.TextChoices):
    MULTIPLE_CHOICE = "multiple_choice", "Multiple choice"
    RADIO = "radio", "Radio"

class Question(models.Model):
    title = models.TextField()
    description = models.TextField(default="")
    question_type = models.TextField(choices=QuestionType)
    chapter_event = models.ForeignKey("ChapterEvent", related_name="questions", on_delete=models.DO_NOTHING)
