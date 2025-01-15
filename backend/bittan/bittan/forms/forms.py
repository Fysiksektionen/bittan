from django import forms
from bittan.models import ChapterEvent

class ChapterEventForm(forms.Form):
    chapter_event = forms.ModelChoiceField(
        queryset=ChapterEvent.objects.all(),
        required=False,
        empty_label="All Chapter Events",
        to_field_name="title"
    )

