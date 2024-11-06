import json

from bittan.models.payment import PaymentStatus

from ..models import ChapterEvent, Ticket, TicketType, Payment

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
