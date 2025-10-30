from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework import serializers

from bittan.models import chapter_event
from bittan.models.chapter_event import ChapterEvent
from bittan.models.question import Question

def get_event_summary(event_id): 
    Question.objects.filter(chapter_event = event_id)

    pass

def get_event_meta():
    pass




def TicketSerializerFilter(serializers.Serializer):
    question = serializers.String


class GetEventTicketsSerializer(serializers.Serializer):
    ticket_type = serializers.IntegerField(required=True)
    count = serializers.IntegerField(required=True, min_value=1)


def get_event_tickets():
    pass
