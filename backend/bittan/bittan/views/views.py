from bittan.models.payment import PaymentStatus

from ..models import ChapterEvent, Ticket, TicketType, Payment

from django.db import models

from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework import serializers

from django.utils import timezone

class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ["id", "price", "title", "description"]

class ChapterEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChapterEvent
        fields = ["id", "title", "description", "event_at", "max_tickets_per_payment", "sales_stop_at", "ticket_types"]

@api_view(['GET'])
def get_chapterevents(request: Request) -> Response:
    now = timezone.now()
    chapter_events = ChapterEvent.objects.filter(sales_stop_at__gt=now).order_by("event_at")
    chapter_events_serialized = ChapterEventSerializer(chapter_events, many=True)
    ticket_types = {ticket_type for chapter_event in chapter_events for ticket_type in chapter_event.ticket_types.all()}
    ticket_types_serialized = TicketTypeSerializer(ticket_types, many=True)
    data = {"chapter_events": chapter_events_serialized.data, "ticket_types": ticket_types_serialized.data}
    return Response(data)

class ValidateTicketRequestSerializer(serializers.Serializer):
    external_id = serializers.CharField()

@api_view(['PUT'])
def validate_ticket(request: Request) -> Response:
    ''' Gets a ticket by its (public) id and gets how many times it has 
    been used. Increases its usage count. Returns how many times the ticket has been used
    excluded from the current time. '''
    valid_ser = ValidateTicketRequestSerializer(data=request.data)
    if valid_ser.is_valid():
        response_data = valid_ser.validated_data
    else:
        return Response(
                "InvalidRequestData",
                status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        ticket = Ticket.objects.get(external_id=response_data["external_id"])
    except Ticket.DoesNotExist:
        return Response({"times_used": -1, "status": "Ticket does not exist"})

    times_used = ticket.times_used
    ticket.times_used += 1 
    ticket.save()
    

    return Response({"times_used": times_used, "status": ticket.payment.status})



    
    
