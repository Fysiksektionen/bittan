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
        expires_at = timezone.now(),
        swish_id = None, 
        status = PaymentStatus.ALIVE,
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


@api_view(['POST'])
def start_payment(request):
    payment_id = request.session["reserved_payment"]
    payment = Payment.objects.get(pk=payment_id)
    

    tickets = payment.ticket_set
    chapter_event = tickets.first().ticket_type.chapterevent_set.first()

    # Kolla att biljetterna fortfarande är giltiga,
    if payment.status != PaymentStatus.ALIVE:
    #   Nej -->  Kolla om det går att skapa nya biljetter
        if tickets.count() > chapter_event.ticket_count():
            # Nej --> Informera den stackars kunden om att den är alldeles för långsam.
            # Skriv något vettigt i responsen så att klient vet att biljetterna är slut. 
            return Response()
        payment.expires_at = timezone.now()
    # Ja --> Skapa biljetter (Lås?), uppdatera session och forsätt
    payment.payment_started = True
    payment.save(update_fields=["payment_started"])
    # Ja --> Frys? Biljetterns och forstätt
    pass
    

    # Hämta/beräkna den datan som Swish behöver (tel nummer, belopp, etc)

    # Interagera med swish, skicka belopp och swish message. Få tillbaka swish_payment_request
 
    # Fråga efter token för swish_id

    return Response(chapter_event.title)