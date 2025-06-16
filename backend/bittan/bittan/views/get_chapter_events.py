from bittan.models import ChapterEvent,TicketType

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
    tickets_left = serializers.SerializerMethodField()

    class Meta:
        model = ChapterEvent
        fields = ["id", "title", "description", "event_at", "max_tickets_per_payment", "sales_stop_at", "ticket_types", "tickets_left"]

    def get_tickets_left(self, obj):
        return obj.total_seats - obj.alive_ticket_count

@api_view(['GET'])
def get_chapter_events(request: Request) -> Response:
    now = timezone.now()
    chapter_events = ChapterEvent.objects.filter(sales_stop_at__gt=now).order_by("event_at")
    chapter_events_serialized = ChapterEventSerializer(chapter_events, many=True)
    ticket_types = {ticket_type for chapter_event in chapter_events for ticket_type in chapter_event.ticket_types.filter(is_visible=True)}
    ticket_types_serialized = TicketTypeSerializer(ticket_types, many=True)
    data = {"chapter_events": chapter_events_serialized.data, "ticket_types": ticket_types_serialized.data}
    return Response(data)

