from bittan.models import Ticket
from bittan.settings import EnvVars, ENV_VAR_NAMES

from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view

import logging

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

