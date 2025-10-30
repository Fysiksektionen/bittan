from bittan.models.payment import PaymentStatus
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone

from bittan.models import Answer, AnswerSelectedOptions, Payment, Ticket, Question, QuestionOption
from bittan.models.question import QuestionType

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

    def validate(self, data):
        if len(data["option_ids"]) != len(data["option_texts"]):
            raise serializers.ValidationError("Id array and text array must be of the same length.")
        return data

class FormSubmissionSerializer(serializers.Serializer):
    session_id = serializers.CharField(required=True)
    form_data = serializers.ListField(child=QuestionSerializer(), required=True)

@api_view(["POST"])
def submit_form(request: Request) -> Response:
	response_data: dict
	valid_ser = FormSubmissionSerializer(data=request.data)
	if valid_ser.is_valid():
		response_data = valid_ser.validated_data
	else:
		return error_helper("InvalidRequestData")
	try:
		payment: Payment = Payment.objects.get(id=response_data["session_id"])
	except ObjectDoesNotExist:
		return error_helper("NoSessionFound")

	if payment.status == "PAID":
		return error_helper("AlreadyPaidPayment")		
    
    # Only supports forms if there are one ticket (for now). 
	ticket = payment.ticket_set.first()
	chapter_event = ticket.chapter_event
	
	if timezone.now() > chapter_event.sales_stop_at:
		return error_helper("FormClosed")

	questions_db = chapter_event.question_set.all()
	form_data_map = {r["question_id"]: r for r in response_data["form_data"]}

	# Validate that all question_options exists and are linked in a valid way in the submission. 
	for qs in form_data_map.values():
		if not chapter_event.question_set.filter(pk=qs["question_id"]).exists():
			return error_helper("QuestionNotFound")

		q_db = chapter_event.question_set.get(pk=qs["question_id"])
		q_opts_db = q_db.questionoption_set
		for q_opt in qs["option_ids"]:
			if not q_opts_db.filter(pk=q_opt).exists():
				return error_helper("QuestionOptionNotFound")

	# Validate that the submitted answer obey constraints on question types. 
	for q in questions_db:
		# Validate radio buttons.
		if q.question_type == QuestionType.RADIO:
			if q.pk not in form_data_map:
				return error_helper("UnansweredMandatory")

			q_ans = form_data_map[q.pk]
			if len(q_ans["option_ids"]) != 1:
				return error_helper("UnansweredMandatory" if len(q_ans["option_ids"]) == 0 else "TooManyOptions")

			chosen_option = q.questionoption_set.get(pk=q_ans["option_ids"][0])
			if chosen_option.has_text and q_ans["option_texts"][0] == "":
				return error_helper("UnansweredMandatory")
		
		# Validate multiple choices.
		if q.question_type == QuestionType.MULTIPLE_CHOICE:
			if q.pk not in form_data_map:
				continue
			
			q_ans = form_data_map[q.pk]
			# Validate text fields multiple choice (mandatory if there are more than 1 option with text, otherwise optional).
			if q.questionoption_set.count() > 1:
				for text, option in zip(q_ans["option_texts"], q_ans["option_ids"]):
					chosen_option = q.questionoption_set.get(pk=option)
					if chosen_option.has_text and text == "":
						return error_helper("UnansweredMandatory")

	# Update everhything at once (!?) if the session is valid. 
	with transaction.atomic():
		# Gets the payment and its related ticket and locks them.
		payment = Payment.objects.select_for_update().get(id=response_data["session_id"])
		ticket = payment.ticket_set.select_for_update().first()

		if payment.status == PaymentStatus.CONFIRMED:
			# Safe early return since no changes has been done.
			return error_helper("FormClosed")
		elif payment.status != PaymentStatus.RESERVED:
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

