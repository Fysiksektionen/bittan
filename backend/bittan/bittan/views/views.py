import json

from bittan.models.ticket import TicketStatus

from ..models import ChapterEvent, Ticket, TicketType

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import random
import string

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
    tickets  = []
    for ticket in response_data["tickets"]:
        tickets.extend(
            Ticket.objects.create(
                external_id=''.join(random.choice(string.ascii_letters + string.digits) for _ in range(4)),
                time_created=timezone.now(),
                payment=None,
                status=TicketStatus.ALIVE,
                ticket_type=TicketType.objects.get(title=ticket["ticket_type"])
            ) for _ in range(ticket["count"])
        )
    request.session["reserved_tickets"] = list([x.pk for x in tickets])
    return Response(status=status.HTTP_200_OK)

