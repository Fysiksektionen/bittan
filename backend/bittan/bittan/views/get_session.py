from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework import serializers, status

from bittan.models import AnswerSelectedOptions, Payment

from django.utils import timezone
from django.db.models import Count, Prefetch

class TicketSerializer(serializers.Serializer):
    ticket_type = serializers.PrimaryKeyRelatedField(read_only=True)
    count = serializers.IntegerField()

class AnswerSelectedOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerSelectedOptions
        fields = ["option"]
    

@api_view(["GET"])
def get_session(request: Request, session_id: str) -> Response:
    payment: Payment
    try:
        payment = Payment.objects.get(id=session_id)
    except Payment.DoesNotExist:
        return Response("Session not found", status=404)

    tickets = payment.ticket_set
    ticket_data = list(
        tickets.values("ticket_type").annotate(count=Count("ticket_type"))
    )
    
    if tickets.count() > 1:
        return Response({
            "status": payment.status,
            "tickets": ticket_data
        })
    
    ticket = tickets.first()
    answers = ticket.answer_set.prefetch_related(
                    Prefetch(
                        'answerselectedoptions_set',
                        queryset=AnswerSelectedOptions.objects.order_by('pk'),
                        to_attr='selected_options_prefetched'
                    )
                )
    answer_data = []
    for answer in answers:
        selected_options = answer.answerselectedoptions_set.all()
        options = [selected_option.question_option.pk for selected_option in selected_options]
        texts = [selected_option.text for selected_option in selected_options]
        answer_data.append(
            {
                "question": answer.question.pk,
                "options": options,
                "texts": texts,
            }
        )
    return Response({
            "status": payment.status,
            "tickets": ticket_data,
            "answers": answer_data
    
        })
