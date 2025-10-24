from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework import serializers

from bittan.models import Answer, Payment, Ticket
 
@api_view(["POST"])
def submit_form(request: Request) -> Response:
    return Response("Hello there")

