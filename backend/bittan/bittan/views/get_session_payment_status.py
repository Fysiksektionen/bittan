from bittan.models.payment import PaymentStatus

from bittan.models import Payment


from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view

@api_view(['GET'])
def get_session_payment_status(request: Request, session_id: str) -> Response:
    try:
        payment = Payment.objects.get(pk=session_id)
    except Payment.DoesNotExist:
        return Response(
                "Session had a payment id, but no such payment existed in the database",
                status=status.HTTP_404_NOT_FOUND,
            )
    if payment.status == PaymentStatus.PAID:
        return Response({"status": payment.status, "mail": payment.email, "reference": payment.swish_id})

    return Response({"status": payment.status, "mail": payment.email})
