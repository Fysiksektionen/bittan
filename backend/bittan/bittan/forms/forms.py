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
    query = forms.CharField(label="Search ticket or payment", max_length=100)

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


class TicketCreationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        ticket_types = kwargs.pop('ticket_types', [])
        super(TicketCreationForm, self).__init__(*args, **kwargs)

        for ticket_type in ticket_types:
            self.fields[f'ticket_type_{ticket_type.id}'] = forms.IntegerField(label=ticket_type.title, min_value=0)
            self.fields[f"ticket_type_{ticket_type.id}_price"] = forms.IntegerField(initial=ticket_type.price, widget=forms.HiddenInput())
        self.fields['email'] = forms.EmailField(label="Email Address")

