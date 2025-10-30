from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework import serializers



def get_event_meta():
    pass


def GetEventStatisticsSerializer(serializers.Serializer):
    chapter_event = serializers.CharField(required = True)

def get_event_statistics(request: Request):
    request_data: dict

    valid_ser = ReserveTicketRequestSerializer(data=request.data)
    if valid_ser.is_valid():
        request_data = valid_ser.event_chapter
    else:
        return Response("InvalidRequestData", status=status.HTTP_400_BAD_REQUEST)

    try:
        chapter_event: ChapterEvent = ChapterEvent.objects.get(id=request_data["chapter_event"])
    except (ObjectDoesNotExist, ValueError):
        return Response(
            "EventDoesNotExist",
            status=status.HTTP_404_NOT_FOUND
        )


def TicketSerializerFilter(serializers.Serializer):
    question = serializers.String


class GetEventTicketsSerializer(serializers.Serializer):
    ticket_type = serializers.IntegerField(required=True)
    count = serializers.IntegerField(required=True, min_value=1)


def get_event_tickets():
    pass
