from django.db import models

class FieldOptions(models.TextChoices):
    MANDATORY = "mandatory", "Mandatory"
    OPTIONAL = "optional", "Optional"
    NO_TEXT = "no_text", "No text"

class QuestionOption(models.Model):
    name = models.TextField()
    description = models.TextField(default="")
    price = models.IntegerField()
    text = models.TextField(choices=FieldOptions)
    question = models.ForeignKey("Question", on_delete=models.DO_NOTHING)


