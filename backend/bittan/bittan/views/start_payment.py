from bittan.models.payment import PaymentMethod, PaymentStatus
from bittan.services.swish.swish_payment_request import SwishPaymentRequest

from bittan.models import Payment

from bittan.services.swish.swish import Swish

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import serializers


from django.utils import timezone
from django.db.models import Sum

import logging

class StartPaymentRequestSerializer(serializers.Serializer):
    session_id = serializers.CharField(required=True)

@api_view(['POST'])
def start_payment(request):
    response_data: dict
    valid_ser = StartPaymentRequestSerializer(data=request.data)
    if valid_ser.is_valid():
        response_data = valid_ser.validated_data
    else:
        return Response(
                "InvalidRequestData",
                status=status.HTTP_400_BAD_REQUEST
            )

    payment_id = response_data["session_id"]

    try:
        payment = Payment.objects.get(pk=payment_id)
    except Payment.DoesNotExist:
        return Response(
                "CouldNotFindSession",
                status=status.HTTP_404_NOT_FOUND
            )

    if payment.status == PaymentStatus.PAID:
        return Response(
                "AlreadyPaidPayment",
                status=status.HTTP_403_FORBIDDEN
            )

    swish = Swish.get_instance() # Gets the swish intstance that is global for the entire application. 
    if payment.payment_started:
        return Response(swish.get_payment_request(payment.swish_id).token)

    tickets = payment.ticket_set.all()

    chapter_event = tickets.first().chapter_event

    if payment.status not in (PaymentStatus.RESERVED, PaymentStatus.FORM_SUBMITTED, PaymentStatus.CONFIRMED):
        # TODO This comparison and update should also happen on the database 
        if chapter_event.fcfs and tickets.count() > chapter_event.total_seats - chapter_event.alive_ticket_count:
             payment.status = PaymentStatus.FAILED_EXPIRED_RESERVATION
             payment.save()
             return Response(
                 "SessionExpired", 
                 status=status.HTTP_408_REQUEST_TIMEOUT
             )
        payment.expires_at = timezone.now() + chapter_event.reservation_duration
        payment.status = PaymentStatus.RESERVED
        payment.save()
    

    good_status = PaymentStatus.RESERVED
    if not chapter_event.fcfs:
        good_status = PaymentStatus.CONFIRMED
    elif chapter_event.question_set.exists():
        good_status = PaymentStatus.FORM_SUBMITTED

    if payment.status != good_status:
        return Response(
            "PaymentNotPayable",
            status=status.HTTP_403_FORBIDDEN
        )
    
    # "Atomically" update the payment status.  
    Payment.objects.filter(
        pk = payment_id,
        status = good_status, # These are just so that we are sure that the payment is in the required status. If it is not get will throw an error and that should be OK. 
        payment_started = False
    ).update(
        payment_started = True
    )

    payment.refresh_from_db()

    # payment.payment_started = True
    logging.info(f"Started payment for payment with id {payment_id}")

    total_price = tickets.aggregate(Sum("ticket_type__price"))["ticket_type__price__sum"]
    
    swish = Swish.get_instance() # Gets the swish intstance that is global for the entire application. 
    
    payment_request: SwishPaymentRequest = swish.create_swish_payment(total_price, chapter_event.swish_message)

    if payment_request.is_failed():
        payment.PaymentStatus = PaymentStatus.FAILED_EXPIRED_RESERVATION
        logging.warning(f"Payment with id {payment_id} did not get correctly initialised with Swish.")
        return Response("PaymentStartFailed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    payment.swish_id = payment_request.id
    payment.payment_method = PaymentMethod.SWISH
    payment.save()
    logging.info(f"Sucessfully initialised payment for payment with id {payment_id} with Swish.")
     
    return Response(payment_request.token)

