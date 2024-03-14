import json

from bittan.models.ticket import TicketStatus
from bittan.models.payment import PaymentStatus

from ..models import ChapterEvent, Ticket, TicketType, Payment

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import random

from django.utils import timezone


@api_view(['POST'])
def reserve_ticket(request):
    response_data: dict = request.data
    reservation_count: int = sum(x["count"] for x in response_data["tickets"])
    chapter_event: ChapterEvent = ChapterEvent.objects.get(pk=response_data["chapter_event"]) 
    if reservation_count > chapter_event.max_tickets - chapter_event.ticket_count:
        return Response(
            status=status.HTTP_403_FORBIDDEN
        )
    payment = Payment.objects.create(
        time_created = timezone.now(),
        swish_id = None, 
        status = PaymentStatus.ALIVE,
        telephone_number = None,
        email = None, 
        total_price = None
    )
    tickets  = []
    for ticket in response_data["tickets"]:
        tickets.extend(
            Ticket.objects.create(
                external_id=''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(6)),
                time_created=timezone.now(),
                payment=payment,
                status=TicketStatus.ALIVE,
                ticket_type=TicketType.objects.get(title=ticket["ticket_type"])
            ) for _ in range(ticket["count"])
        )
    payment.total_price = sum(x.ticket_type.price for x in tickets)
    payment.save(update_fields=["total_price"])
    request.session["reserved_payment"] = payment.pk
    return Response(status=status.HTTP_200_OK)
