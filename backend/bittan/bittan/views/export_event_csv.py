import csv

from django.http import HttpResponse, Http404
from rest_framework.decorators import api_view
from rest_framework import serializers, status
from bittan.models import ChapterEvent, Ticket, Payment, TicketType
from bittan.models.payment import PaymentStatus
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda user: user.is_staff)
@api_view(["GET"])
def export_chapter_event_csv(request, chapter_event_id):
    try:
        chapter_event = ChapterEvent.objects.get(id=chapter_event_id)
    except ChapterEvent.DoesNotExist:
        return Http404("ChapterEvent not found")

    tickets = Ticket.objects.filter(
        chapter_event = chapter_event,
        payment__status = PaymentStatus.PAID or PaymentStatus.FAILED_ADMIN
    ).select_related(
        "ticket_type", 
        "payment"
    ).values(
        "payment__id", 
        "payment__time_paid", 
        "ticket_type__title",
        "payment__email",
        "payment__status", 
        "payment__payment_method",
        "ticket_type__price"
    ).iterator()


    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = f'attachment; filename="BitTan_export_{chapter_event.title}.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "payment_id",
        "time",
        "ticket_type",
        "email",
        "status", 
        "payment_method",
        "ticket_price"
    ])

    for ticket in tickets:
        writer.writerow([
            ticket["payment__id"],
            ticket["payment__time_paid"],
            ticket["ticket_type__title"],
            ticket["payment__email"],
            ticket["payment__status"], 
            ticket["payment__payment_method"],
            ticket["ticket_type__price"],
        ])
    
    return response
