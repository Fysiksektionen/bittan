from bittan.models.payment import PaymentStatus
from bittan.services.swish.swish_payment_request import PaymentStatus as SwishPaymentStatus

from bittan.models import ChapterEvent, Ticket, TicketType, Payment
from bittan.mail import mail_bittan_developers

from bittan.services.swish.swish import Swish

from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework import serializers

import random

from django.utils import timezone
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

import logging

class TicketsSerializer(serializers.Serializer):
    ticket_type = serializers.IntegerField(required=True)
    count = serializers.IntegerField(required=True, min_value=1)

class ReserveTicketRequestSerializer(serializers.Serializer):
    chapter_event = serializers.CharField(required = True)
    tickets = serializers.ListField(child=TicketsSerializer())
    email_address = serializers.EmailField(max_length=255)
    session_id = serializers.CharField(required=False)

@api_view(['POST'])
def reserve_ticket(request: Request) -> Response:
    response_data: dict

    valid_ser = ReserveTicketRequestSerializer(data=request.data)
    if valid_ser.is_valid():
        response_data = valid_ser.validated_data
    else:
        return Response(
                "InvalidRequestData",
                status=status.HTTP_400_BAD_REQUEST
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
    
    # Check if the current session already has a payment with associated tickets. 
    payment_id = response_data.get("session_id", None)
    if payment_id != None:
        try: 
            payment = Payment.objects.get(pk=payment_id, status=PaymentStatus.RESERVED)
            # If the payment is already started then attempt to cancel it. 
            if payment.payment_started:
                swish = Swish.get_instance() 
                cancel_status = swish.cancel_payment(payment.swish_id)
                # Checks if the cancel_status is still CREATED. This should never happen. 
                if cancel_status == SwishPaymentStatus.CREATED:
                    logging.error(f"Swish did not cancel a payment that should be cancelled. Swish payment reference: {payment.swish_id}")
                    return Response(status=500)
            else:
                # Since the payment is not started just failing it should not have any severe consequences.
                payment.status = PaymentStatus.FAILED_EXPIRED_RESERVATION
                payment.save()
        except Payment.DoesNotExist:
            pass

    
    if reservation_count > chapter_event.max_tickets_per_payment:
        return Response(
            "TooManyTickets",
            status=status.HTTP_403_FORBIDDEN
        )

    if reservation_count > chapter_event.total_seats - chapter_event.alive_ticket_count:
        return Response(
            {
                "error": "OutOfTickets", 
                "tickets_left": chapter_event.total_seats - chapter_event.alive_ticket_count
            },
            status=status.HTTP_403_FORBIDDEN
        )

    payment = Payment.objects.create(
        expires_at = timezone.now() + chapter_event.reservation_duration,
        swish_id = None, 
        status = PaymentStatus.RESERVED,
        email = response_data["email_address"], 
    )

    for ticket in tickets:
        try:
            ticket_type = TicketType.objects.get(pk=ticket["ticket_type"], is_visible=True)
        except ObjectDoesNotExist:
            return Response(
                "TicketTypeDoesNotExist",
                status=status.HTTP_404_NOT_FOUND
            )
        for _ in range(ticket["count"]):
            # Attempts to create a ticket a maximum of 1000 times. This is to ensure that the external_id of the ticket is guaranteed to be unique. 
            for _ in range(1000):
                try:
                    Ticket.objects.create(
                            external_id=''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(6)),
                            time_created=timezone.now(),
                            payment=payment,
                            ticket_type=ticket_type,
                            chapter_event=chapter_event
                        )
                except IntegrityError as e:
                    continue
                break
            else: 
                logging.error("Failed to generate a ticket external id. This should never happen.")
                mail_bittan_developers(
                    f"Failed to generate ticket external id at {timezone.now().strftime("%Y-%m-%d %H:%M:%S")} for payment with id {payment_id}", 
                    "Failed to generate ticket external id. "
                ) 
                return Response(status=500) # Returns status internal server error. 
    
    return Response(payment.pk, status=status.HTTP_201_CREATED)

