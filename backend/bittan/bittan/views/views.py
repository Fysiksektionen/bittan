from bittan.models.payment import PaymentStatus
from bittan.services.swish.swish_payment_request import SwishPaymentRequest

from ..models import ChapterEvent, Ticket, TicketType, Payment

from bittan.services.swish import Swish

from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework import serializers

import random

from django.utils import timezone
from django.db.utils import IntegrityError
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist

import logging

class ReserveTicketTicketsSerializer(serializers.Serializer):
    ticket_type = serializers.CharField(required=True)
    count = serializers.IntegerField(required=True, min_value=0)

class ValidateReserveTicketSerializer(serializers.Serializer):
    chapter_event = serializers.CharField(required = True)
    tickets = serializers.ListField(child=ReserveTicketTicketsSerializer())


@api_view(['POST'])
def reserve_ticket(request: Request) -> Response:
    response_data: dict

    valid_ser = ValidateReserveTicketSerializer(data=request.data)
    if valid_ser.is_valid():
        response_data = valid_ser.validated_data
    else:
        return Response(
                "InvalidRequestData",
                status=status.HTTP_403_FORBIDDEN
            )

    event_id: int = response_data["chapter_event"]
    tickets: list = response_data["tickets"]

#   if min(x["count"] for x in tickets) < 1: 
#       return Response(
#           "NegativeTickets",
#           status=status.HTTP_403_FORBIDDEN
#       )
    
    reservation_count: int = sum(x["count"] for x in tickets)
    
    try:
        chapter_event: ChapterEvent = ChapterEvent.objects.get(id=event_id)
    except (ObjectDoesNotExist, ValueError):
        return Response(
            "EventDoesNotExist",
            status=status.HTTP_404_NOT_FOUND
        )
    
    if reservation_count > chapter_event.max_tickets - chapter_event.alive_ticket_count:
        return Response(
            "OutOfTickets", 
            status=status.HTTP_403_FORBIDDEN
        )
    

    payment = Payment.objects.create(
        expires_at = timezone.now() + chapter_event.reservation_duration,
        swish_id = None, 
        status = PaymentStatus.RESERVED,
        email = None, 
    )

    for ticket in tickets:
        for _ in range(ticket["count"]):
            for _ in range(1000):
                try:
                    Ticket.objects.create(
                            external_id=''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(6)),
                            time_created=timezone.now(),
                            payment=payment,
                            ticket_type=TicketType.objects.get(title=ticket["ticket_type"], is_visible=True)
                        )
                except ObjectDoesNotExist:
                    return Response(
                        "TicketTypeDoesNotExist",
                        status=status.HTTP_404_NOT_FOUND
                    )
                except IntegrityError as e:
                    continue
                break
            else: 
                logging.critical("Failed to generate a ticket external id. This should never happen.")
                return Response(status=500) # Returns status internal server error. 
    request.session["reserved_payment"] = payment.pk
    return Response(status=status.HTTP_201_CREATED)


@api_view(['POST'])
def start_payment(request):
    response_data: dict = request.data
    payment_id = request.session["reserved_payment"]
    payment = Payment.objects.get(pk=payment_id)

    # TODO Verify that the payment is not already started. IMPORTANT since someone might be able 
    # to pay twice for the same tickets otherwise. 

    tickets = payment.ticket_set
    chapter_event = tickets.first().ticket_type.chapterevent_set.first()

    # Kolla att biljetterna fortfarande är giltiga,
    if payment.status != PaymentStatus.RESERVED:
        # Nej -->  Kolla om det går att skapa nya biljetter
        if tickets.count() > chapter_event.max_tickets - chapter_event.alive_ticket_count:
            # Nej --> Informera den stackars kunden om att den är alldeles för långsam.
            # Skriv något vettigt i responsen så att klient vet att biljetterna är slut. 
            return Response(
                "SessionExpired", 
                status=status.HTTP_403_FORBIDDEN
            )
        # Ja --> Skapa biljetter (Lås?), uppdatera session och forsätt
        payment.expires_at = timezone.now() + chapter_event.reservation_duration
    # Ja --> Starta payment biljetterns och forstätt
    payment.payment_started = True
    # TODO Verifiera att mailaddressen är en riktig mailaddress.
    payment.email = response_data["email_address"]
    payment.save()

    # Hämta/beräkna den datan som Swish behöver (belopp, etc)
    total_price = tickets.aggregate(Sum("ticket_type__price"))["ticket_type__price__sum"]
    
    # TODO eventuell felhantering inför snack med swish här. Även felhantering efter.
    # Interagera med swish, skicka belopp och swish message. Få tillbaka swish_payment_request
    swish = Swish.get_instance() # Detta hämtar swish instansen som är global över hela bittan. I den här kan saker anropas. 
    
    # Används swish-instansen för att skapa ett payment. metod create_swish_payment(self, amount: int, message="") 
    payment_request: SwishPaymentRequest = swish.create_swish_payment(total_price, chapter_event.swish_message)

    # Fråga efter token för swish_id och skicka tillbaka. 
    return Response(payment_request.token)
