from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, F, Sum
from bittan.forms.forms import ChapterEventForm
from bittan.models import ChapterEvent, Ticket
from bittan.models.payment import PaymentStatus

@login_required
@user_passes_test(lambda u: u.groups.filter(name="organisers").count())
def staff_dashboard(request):
    form = ChapterEventForm(request.GET or None)
    chapter_events = ChapterEvent.objects.all()
    ticket_type_infos = None
    total_values = None

    if form.is_valid():
        selected_chapter_event = form.cleaned_data.get("chapter_event")
        if selected_chapter_event:
            chapter_event = get_object_or_404(ChapterEvent, pk=selected_chapter_event.pk)
            ticket_type_infos = chapter_event.ticket_set.filter(
                payment__status = PaymentStatus.PAID, 
                chapter_event = selected_chapter_event
            ).values("ticket_type", "ticket_type__title").annotate(
                ticket_count=Count("id"),
                total_price=F("ticket_count") * F("ticket_type__price")
            )        
        else:
            ticket_type_infos = Ticket.objects.filter(
                payment__status = PaymentStatus.PAID, 
            ).values("ticket_type", "ticket_type__title").annotate(
                ticket_count=Count("id"),
                total_price=F("ticket_count") * F("ticket_type__price")
            )
        total_values = ticket_type_infos.aggregate(
                total_ticket_count=Sum("ticket_count"),
                all_ticket_price=Sum("total_price")
            )


        print(total_values)


    return render(request, "staff_dashboard.html", {"form": form, "chapter_events":chapter_events, "ticket_types":ticket_type_infos, "total_values":total_values})
