import json

from bittan.models.payment import PaymentStatus

from ..models import ChapterEvent, Ticket, TicketType, Payment

from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
import random

from django.utils import timezone
from django.db.utils import IntegrityError
from django.db.models import Sum

import logging


@api_view(['POST'])
def reserve_ticket(request: Request) -> Response:
    response_data: dict = request.data
    reservation_count: int = sum(x["count"] for x in response_data["tickets"])
    chapter_event: ChapterEvent = ChapterEvent.objects.get(id=response_data["chapter_event"])
    if reservation_count > chapter_event.max_tickets - chapter_event.alive_ticket_count:
        return Response(
            "outOfTickets", 
            status=status.HTTP_403_FORBIDDEN
        )
    payment = Payment.objects.create(
        expires_at = timezone.now() + chapter_event.reservation_duration,
        swish_id = None, 
        status = PaymentStatus.RESERVED,
        email = None, 
    )
    tickets  = []
    for ticket in response_data["tickets"]:
        for _ in range(ticket["count"]):
            for _ in range(1000):
                try: 
                    tickets.append(
                        Ticket.objects.create(
                            external_id=''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(6)),
                            time_created=timezone.now(),
                            payment=payment,
                            ticket_type=TicketType.objects.get(title=ticket["ticket_type"])
                        )
                    )
                except IntegrityError as e:
                    continue
                break
            else: 
                logging.critical("Failed to generate a ticket external id. This should never happen.")
                return Response(status=500) # Returns status internal server error. 
    request.session["reserved_payment"] = payment.pk
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def start_payment(request):
    payment_id = request.session["reserved_payment"]
    payment = Payment.objects.get(pk=payment_id)

    tickets = payment.ticket_set
    chapter_event = tickets.first().ticket_type.chapterevent_set.first()

    # Kolla att biljetterna fortfarande är giltiga,
    if payment.status != PaymentStatus.RESERVED:
        # Nej -->  Kolla om det går att skapa nya biljetter
        if tickets.count() > chapter_event.max_tickets - chapter_event.alive_ticket_count:
            # Nej --> Informera den stackars kunden om att den är alldeles för långsam.
            # Skriv något vettigt i responsen så att klient vet att biljetterna är slut. 
            return Response()
        # Ja --> Skapa biljetter (Lås?), uppdatera session och forsätt
        payment.expires_at = timezone.now() + chapter_event.reservation_duration
    # Ja --> Starta payment biljetterns och forstätt
    payment.payment_started = True
    payment.save(update_fields=["payment_started"])

    # Hämta/beräkna den datan som Swish behöver (belopp, etc)
    total_price = tickets.aggregate(Sum("ticket_type__pri>ce"))["ticket_type__price__sum"]

    # Interagera med swish, skicka belopp och swish message. Få tillbaka swish_payment_request
 
    # Fråga efter token för swish_id

    return Response(total_price)
