from bittan.models.payment import PaymentStatus

from ..models import ChapterEvent, Ticket, TicketType, Payment

from django.db import models

from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework import serializers

from django.utils import timezone

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

class ValidateValidateTicketSerializer(serializers.Serializer):
    external_id = serializers.CharField()

@api_view(['PUT'])
def validate_ticket(request: Request) -> Response:

    valid_ser = ValidateValidateTicketSerializer(data=request.data)
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
    # Gets a ticket by its (public) id and gets how many times it has 
    # been used. Increases its usage count. Returns how many times the ticket has been used
    # excluded from the current time. 



    
    
