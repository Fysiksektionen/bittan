from bittan.models.payment import PaymentStatus

from bittan.models import Ticket, Payment


from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view

@api_view(['GET'])
def get_session_payment_status(request: Request) -> Response:
    payment_primary_key = request.session.get("reserved_payment")
    if payment_primary_key == None:
        return Response(
                "No ticket attatched to session",
                status=status.HTTP_400_BAD_REQUEST
            )

    try:
        payment = Payment.objects.get(pk=payment_primary_key)
    except Ticket.DoesNotExist:
        return Response(
                "Session had a payment id, but no such payment existed in the database",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    if payment.status == PaymentStatus.PAID:
        return Response({"status": payment.status, "mail": payment.email, "reference": payment.swish_id})

    return Response({"status": payment.status, "mail": payment.email})
