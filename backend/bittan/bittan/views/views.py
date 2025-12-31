from bittan.models.payment import PaymentMethod, PaymentStatus
from bittan.services.swish.swish_payment_request import SwishPaymentRequest, PaymentStatus as SwishPaymentStatus

from bittan.models import ChapterEvent, Ticket, TicketType, Payment
from bittan.mail import mail_bittan_developers

from bittan.services.swish.swish import Swish
from bittan.settings import EnvVars, ENV_VAR_NAMES

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
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import user_passes_test

import logging
import csv

class TicketsSerializer(serializers.Serializer):
    ticket_type = serializers.IntegerField(required=True)
    count = serializers.IntegerField(required=True, min_value=1)

class ReserveTicketRequestSerializer(serializers.Serializer):
    chapter_event = serializers.CharField(required = True)
    tickets = serializers.ListField(child=TicketsSerializer())

@api_view(['GET'])
def get_session_payment_status(request: Request) -> Response:
    payment_primary_key = request.session.get("reserved_payment")
    if payment_primary_key == None:
        return Response(
                "No ticket attatched to session",
                status=status.HTTP_400_BAD_REQUEST
            )

    try:
        payment = Payment.objects.get(pk=payment_primary_key)
    except Ticket.DoesNotExist:
        return Response(
                "Session had a payment id, but no such payment existed in the database",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    if payment.status == PaymentStatus.PAID:
        return Response({"status": payment.status, "mail": payment.email, "reference": payment.swish_id})

    return Response({"status": payment.status, "mail": payment.email})

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
    payment_id = request.session.get("reserved_payment")
    if payment_id != None:
        try: 
            payment = Payment.objects.get(pk=payment_id)
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
        
        request.session.delete()

    
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
        email = None, 
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

    if payment.status == PaymentStatus.PAID.value:
        return Response(
                "AlreadyPaidPayment",
                status=status.HTTP_403_FORBIDDEN
            )

    swish = Swish.get_instance() # Gets the swish intstance that is global for the entire application. 
    if payment.payment_started:
        return Response(swish.get_payment_request(payment.swish_id).token)

    tickets = payment.ticket_set.all()

    chapter_event = tickets.first().chapter_event

    if payment.status != PaymentStatus.RESERVED:
        if tickets.count() > chapter_event.total_seats - chapter_event.alive_ticket_count:
             payment.status = PaymentStatus.FAILED_EXPIRED_RESERVATION
             payment.save()
             return Response(
                 "SessionExpired", 
                 status=status.HTTP_408_REQUEST_TIMEOUT
             )
        payment.expires_at = timezone.now() + chapter_event.reservation_duration
        payment.status = PaymentStatus.RESERVED
        payment.save()

    payment.payment_started = True
    payment.email = response_data["email_address"]
    payment.save()
    logging.info(f"Started payment for payment with id {payment_id}")

    total_price = tickets.aggregate(Sum("ticket_type__price"))["ticket_type__price__sum"]
    
    swish = Swish.get_instance() # Gets the swish intstance that is global for the entire application. 
    
    payment_request: SwishPaymentRequest = swish.create_swish_payment(total_price, chapter_event.swish_message)

    if payment_request.is_failed():
        payment.PaymentStatus = PaymentStatus.FAILED_EXPIRED_RESERVATION
        logging.warning(f"Payment with id {payment_id} did not get correctly initialised with Swish.")
        return Response("PaymentStartFailed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    payment.swish_id = payment_request.id
    payment.payment_method = PaymentMethod.SWISH
    payment.save()
    logging.info(f"Sucessfully initialised payment for payment with id {payment_id} with Swish.")
     
    return Response(payment_request.token)

class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ["id", "price", "title", "description"]

class ChapterEventSerializer(serializers.ModelSerializer):
    tickets_left = serializers.SerializerMethodField()

    class Meta:
        model = ChapterEvent
        fields = ["id", "title", "description", "event_at", "max_tickets_per_payment", "sales_stop_at", "ticket_types", "tickets_left"]

    def get_tickets_left(self, obj):
        return obj.total_seats - obj.alive_ticket_count

@api_view(['GET'])
def get_chapterevents(request: Request) -> Response:
    now = timezone.now()
    chapter_events = ChapterEvent.objects.filter(sales_stop_at__gt=now).order_by("event_at")
    chapter_events_serialized = ChapterEventSerializer(chapter_events, many=True)
    ticket_types = {ticket_type for chapter_event in chapter_events for ticket_type in chapter_event.ticket_types.filter(is_visible=True)}
    ticket_types_serialized = TicketTypeSerializer(ticket_types, many=True)
    data = {"chapter_events": chapter_events_serialized.data, "ticket_types": ticket_types_serialized.data}
    return Response(data)

class ValidateTicketRequestSerializer(serializers.Serializer):
    external_id = serializers.CharField()
    password = serializers.CharField()
    use_ticket = serializers.BooleanField()

@api_view(['PUT'])
def validate_ticket(request: Request) -> Response:
    ''' Gets a ticket by its (public) id and gets how many times it has 
    been used. Increases its usage count. Returns how many times the ticket has been used
    excluded from the current time. '''
    valid_ser = ValidateTicketRequestSerializer(data=request.data)
    if valid_ser.is_valid():
        request_data = valid_ser.validated_data
    else:
        return Response(
                "InvalidRequestData",
                status=status.HTTP_400_BAD_REQUEST
            )

    # No hashing, not super important endpoint + HTTPS encrypts 
    if request_data["password"] != EnvVars.get(ENV_VAR_NAMES.TICKET_VALIDATION_PASSWORD):
        return Response("Incorrect password", status.HTTP_401_UNAUTHORIZED) 
    
    try:
        ticket = Ticket.objects.get(external_id=request_data["external_id"])
    except Ticket.DoesNotExist:
        return Response({"times_used": -1, "status": "Ticket does not exist"}, status.HTTP_404_NOT_FOUND)

    logging.info(f"Scanned ticket {ticket.external_id}. Used? {request_data["use_ticket"]}")

    chapter_event = ticket.chapter_event.title
    times_used = ticket.times_used

    if request_data["use_ticket"]:
        ticket.times_used += 1 
        ticket.save()

    return Response({"external_id": ticket.external_id, "times_used": times_used, "chapter_event": chapter_event, "status": ticket.payment.status})


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

