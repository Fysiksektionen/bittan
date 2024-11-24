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

class TicketsSerializer(serializers.Serializer):
    ticket_type = serializers.CharField(required=True)
    count = serializers.IntegerField(required=True, min_value=0)

class ReserveTicketRequestSerializer(serializers.Serializer):
    chapter_event = serializers.CharField(required = True)
    tickets = serializers.ListField(child=TicketsSerializer())


@api_view(['POST'])
def reserve_ticket(request: Request) -> Response:
    response_data: dict

    valid_ser = ReserveTicketRequestSerializer(data=request.data)
    if valid_ser.is_valid():
        response_data = valid_ser.validated_data
    else:
        return Response(
                "InvalidRequestData",
                status=status.HTTP_403_FORBIDDEN
            )

    event_id: int = response_data["chapter_event"]
    tickets: list = response_data["tickets"]
    
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
            # Attempts to create a ticket a maximum of 1000 times. This is to ensure that the external_id of the ticket is guaranteed to be unique. 
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


class StartPaymentRequestSerializer(serializers.Serializer):
    email_address = serializers.EmailField(max_length=255)


@api_view(['POST'])
def start_payment(request):
    response_data: dict

    valid_ser = StartPaymentRequestSerializer(data=request.data)
    if valid_ser.is_valid():
        response_data = valid_ser.validated_data
    else:
        return Response(
                "InvalidRequestData",
                status=status.HTTP_400_BAD_REQUEST
            )

    payment_id = request.session.get("reserved_payment")
    if payment_id == None:
        return Response(
                "InvalidSession",
                status=status.HTTP_400_BAD_REQUEST
            )

    payment = Payment.objects.get(pk=payment_id)

    if payment.payment_started:
        return Response(
                "AlreadyPaidPayment",
                status=status.HTTP_403_FORBIDDEN
            )

    tickets = payment.ticket_set

    # Gets the chapter event from the users ticket.
    chapter_event = tickets.first().ticket_type.chapterevent_set.first()

    if payment.status != PaymentStatus.RESERVED:
        if tickets.count() > chapter_event.max_tickets - chapter_event.alive_ticket_count:
            return Response(
                "SessionExpired", 
                status=status.HTTP_408_REQUEST_TIMEOUT
            )
        payment.expires_at = timezone.now() + chapter_event.reservation_duration

    payment.payment_started = True

    payment.email = response_data["email_address"]
    payment.save()

    total_price = tickets.aggregate(Sum("ticket_type__price"))["ticket_type__price__sum"]
    
    # TODO eventuell felhantering inför snack med swish här. Även felhantering efter.
    # Interagera med swish, skicka belopp och swish message. Få tillbaka swish_payment_request
    swish = Swish.get_instance() # Detta hämtar swish instansen som är global över hela bittan. I den här kan saker anropas. 
    
    # Används swish-instansen för att skapa ett payment. metod create_swish_payment(self, amount: int, message="") 
    payment_request: SwishPaymentRequest = swish.create_swish_payment(total_price, chapter_event.swish_message)

    # Fråga efter token för swish_id och skicka tillbaka. 

    return Response(payment_request.token)

class ChapterEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChapterEvent
        fields = ["id", "title", "description", "event_at"]

@api_view(['GET'])
def get_chapterevents(request: Request) -> Response:
    now = timezone.now()
    chapterevents = ChapterEvent.objects.filter(sales_stop_at__gt=now).order_by("event_at")
    s = ChapterEventSerializer(chapterevents, many=True)
    return Response(s.data)

