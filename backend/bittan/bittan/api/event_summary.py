from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework import serializers
from django.db import connection

from bittan.models import chapter_event
from bittan.models.chapter_event import ChapterEvent
from bittan.models.question import Question

@api_view(['GET'])
def get_question_summary(request: Request, question_id): 
    print(question_id)
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH per_answer AS (
                SELECT
                    answer.id AS answer_id,
                    array_agg(question_option.id ORDER BY question_option.name) AS combination_ids, 
                    array_agg(question_option.name ORDER BY question_option.name) AS combination_names
                FROM bittan_answer AS answer 
                LEFT JOIN bittan_answerselectedoptions AS selected_option ON selected_option.answer_id = answer.id 
                LEFT JOIN bittan_questionoption question_option ON question_option.id = selected_option.question_option_id
                WHERE answer.question_id = %s 
                GROUP BY answer.id
            )
            SELECT
                combination_ids,
                combination_names,
                COUNT(*)
            FROM per_answer
            GROUP BY (combination_ids, combination_names)
        """, [question_id])
        results = list(map(lambda entry: {"combination_ids": entry[0], "combination_names": entry[1], "combination_count": entry[2]}, cursor.fetchall()))

    # print(type(results))
    return Response(results)
    # print(results)


# def get_event_meta():
#     pass
#
#
#
# def TicketSerializerFilter(serializers.Serializer):
#     question = serializers.String
#
#
# class GetEventTicketsSerializer(serializers.Serializer):
#     ticket_type = serializers.IntegerField(required=True)
#     count = serializers.IntegerField(required=True, min_value=1)
#
#
# def get_event_tickets():
#     pass
