from django import forms
from bittan.models import ChapterEvent, Payment, Ticket

class ChapterEventForm(forms.Form):
    chapter_event = forms.ModelChoiceField(
        queryset=ChapterEvent.objects.all(),
        required=False,
        empty_label="All Chapter Events",
        to_field_name="title"
    )

class SearchForm(forms.Form):
    query = forms.CharField(
        label="Search ticket or payment",
        widget=forms.TextInput(attrs={"class": "search-input"})
    )

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["email", "status"] 

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["status"].widget.attrs.update({"class": "form-control"})

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["ticket_type", "chapter_event"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["ticket_type"].widget.attrs.update({"class": "form-control"})
        self.fields["chapter_event"].widget.attrs.update({"class": "form-control"})

class ChapterEventDropdownTicketCreation(forms.Form):
    chapter_event = forms.ModelChoiceField(
        queryset=ChapterEvent.objects.all(),
        empty_label="No event",
    )

    @staticmethod
    def label_from_instance(obj):
        return str(obj)

