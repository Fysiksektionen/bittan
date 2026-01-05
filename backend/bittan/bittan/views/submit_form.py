from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework import serializers

from django.db import transaction
from django.utils import timezone

from bittan.models import Answer, AnswerSelectedOptions, ChapterEvent, Payment, Ticket, Question, QuestionOption
from bittan.models.question import QuestionType
from bittan.models.payment import PaymentStatus

from typing import Dict, Optional, Tuple, TypedDict, List, Union

class QuestionData(TypedDict):
	question_id: int
	option_ids: List[int]
	option_texts: List[str]

class FormData(TypedDict):
	session_id: str
	form_data: List[QuestionData]

CODE_MAPPINGS = {
	"InvalidRequestData": status.HTTP_400_BAD_REQUEST,
    "UnansweredMandatory": status.HTTP_400_BAD_REQUEST,
    "TooManyOptions": status.HTTP_400_BAD_REQUEST,
    "SessionExpired": status.HTTP_403_FORBIDDEN,
    "FormClosed": status.HTTP_403_FORBIDDEN,
    "AlreadyPaidPayment": status.HTTP_403_FORBIDDEN,
    "NoSessionFound": status.HTTP_404_NOT_FOUND,
    "QuestionNotFound": status.HTTP_404_NOT_FOUND,
    "QuestionOptionNotFound": status.HTTP_404_NOT_FOUND
}
error_helper = lambda msg: Response(msg, CODE_MAPPINGS[msg])
 
class QuestionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(required=True)
    option_ids = serializers.ListField(child=serializers.IntegerField(), required=True)
    option_texts = serializers.ListField(child=serializers.CharField(allow_blank=True), required=True)

    def validate(self, attrs):
        if len(attrs["option_ids"]) != len(attrs["option_texts"]):
            raise serializers.ValidationError("Id array and text array must be of the same length.")
        return attrs

class FormSubmissionSerializer(serializers.Serializer):
    session_id = serializers.CharField(required=True)
    form_data = serializers.ListField(child=QuestionSerializer(), required=True)

def validate_payment(
		session_id: str
	) -> Union[Response, Payment]:
	"""
		Validates that a payment exists and is valid for form submission. 
	"""
	try:
		payment: Payment = Payment.objects.get(id=session_id)
	except Payment.DoesNotExist:
		return error_helper("NoSessionFound")

	if payment.status == PaymentStatus.PAID:
		return error_helper("AlreadyPaidPayment")
	
	return payment

def validate_event(
		chapter_event: ChapterEvent
	) -> Optional[Response]:
	if timezone.now() > chapter_event.sales_stop_at:
		return error_helper("FormClosed")
	return None

def validate_questions(
		form_data_map: Dict[int, QuestionData],
		chapter_event: ChapterEvent
	) -> Optional[Response]:
	# Validates that all question_options in the submmission exists and are linked in a valid way
	for qs in form_data_map.values():
		if not chapter_event.question_set.filter(pk=qs["question_id"]).exists():
			return error_helper("QuestionNotFound")
		
		q_db = chapter_event.question_set.get(pk=qs["question_id"])
		q_opts_db = q_db.questionoption_set
		for q_opt in qs["option_ids"]:
			if not q_opts_db.filter(pk=q_opt).exists():
				return error_helper("QuestionOptionNotFound")
	
	questions_db = chapter_event.question_set.all()
	for q in questions_db:
		# Validate radio buttons. 
		if q.question_type == QuestionType.RADIO:
			if q.pk not in form_data_map:
				return error_helper("UnansweredMandatory")
			
			q_ans = form_data_map[q.pk]
			if len(q_ans["option_ids"]) != 1:
				return error_helper(
					"UnansweredMandatory" if len(q_ans["option_ids"]) == 0
					else "TooManyOptions"
				)

			chosen_option = q.questionoption_set.get(pk=q_ans["option_ids"][0])
			if chosen_option.has_text and q_ans["option_texts"][0] == "":
				return error_helper("UnansweredMandatory")
		
		# Validate multiple choices.
		if q.question_type == QuestionType.MULTIPLE_CHOICE:
			# Multiple choice is always non mandatory. 
			if q.pk not in form_data_map:
				continue

			q_ans = form_data_map[q.pk]
			# Validate text fields multiple choice (mandatory if there are more than 1 option with text, otherwise optional).
			if q.questionoption_set.count() > 1: 
				for text, option in zip(q_ans["option_texts"], q_ans["option_ids"]):
					chosen_option = q.questionoption_set.get(pk=option)
					if chosen_option.has_text and text == "":
						return error_helper("UnansweredMandatory")

@api_view(["POST"])
def submit_form(request: Request) -> Response:
	response_data: dict
	valid_ser = FormSubmissionSerializer(data=request.data)
	if valid_ser.is_valid():
		response_data = valid_ser.validated_data
	else:
		return error_helper("InvalidRequestData")

	payment = validate_payment(response_data["session_id"])
	if isinstance(payment, Response):
		return payment
    
    # Only supports forms if there are one ticket (for now). 
	ticket = payment.ticket_set.first()
	chapter_event = ticket.chapter_event
	ch_error = validate_event(chapter_event)
	if ch_error:
		return ch_error

	form_data_map: Dict[int, QuestionData] = {
		r["question_id"]: r for r in response_data["form_data"]
	}

	q_errors = validate_questions(form_data_map, chapter_event)	
	if q_errors:
		return q_errors

	# Update everhything at once (!?) if the session is valid. 
	with transaction.atomic():
		# Gets the payment and its related ticket and locks them.
		payment = Payment.objects.select_for_update().get(id=response_data["session_id"])
		ticket = payment.ticket_set.select_for_update().first()

		if payment.status == PaymentStatus.CONFIRMED:
			# Safe early return since no changes has been done.
			return error_helper("FormClosed")
		elif payment.status not in (PaymentStatus.RESERVED, PaymentStatus.FORM_SUBMITTED):
			if payment.status != PaymentStatus.FAILED_EXPIRED_RESERVATION:
				# Safe early return since no changes has been done.
				return error_helper("SessionExpired")
			if chapter_event.fcfs and chapter_event.total_seats - chapter_event.alive_ticket_count < 1:
				payment.status = PaymentStatus.FAILED_EXPIRED_RESERVATION
				payment.save()
				return error_helper("SessionExpired")
			payment.expires_at = timezone.now() + chapter_event.reservation_duration
			payment.status = PaymentStatus.RESERVED


		for q in ticket.chapter_event.question_set.all():
			answer: Answer
			if ticket.answer_set.filter(question=q).exists():
				answer = ticket.answer_set.get(question=q)
			else:
				answer = Answer.objects.create(question=q, ticket=ticket)

			submitted_answer = form_data_map[q.pk]
			for text, option_id in zip(submitted_answer["option_texts"], submitted_answer["option_ids"]):
				AnswerSelectedOptions.objects.create(
					answer=answer,
					question_option=QuestionOption.objects.get(pk=option_id),
					text=text
				)
		payment.status = PaymentStatus.FORM_SUBMITTED
		payment.save()

	return Response(status=status.HTTP_200_OK)

