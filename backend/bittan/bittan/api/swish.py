from rest_framework import status 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from ..services.swish import Swish, SwishPaymentRequestResponse
from ..models.swish_payment_request import PaymentStatus, PaymentErrorCode, SwishPaymentRequestModel
from datetime import datetime
from enum import Enum




@api_view(['POST'])
def swish_callback(request: Request):
	print("Tog emot en request från swish:")
	swish_callback = SwishPaymentRequestResponse(request.data)

	model = SwishPaymentRequestModel.objects.get(pk=swish_callback.id)
	Swish.get_instance().update_payment_request(swish_callback)

	# reference = request.data.get("paymentReference")
	# response_code = PaymentResponseCode.from_swish_reponse_code(request.data.get('status'))
	# # if request.status
	# print(response_code)

	# Swish.get_instance().callback_function(reference, response_code)
	return Response("Hello :D", status=status.HTTP_201_CREATED)


@api_view(['POST'])
def make_dummy_request(request: Request):
	resp = Swish.get_instance().create_swish_payment(123, "Hejsan")
	print("Skapade betalning")
	print(f'id: {resp.id}, token: {resp.swish_token}')
	return Response("Skapade swish request", status=status.HTTP_201_CREATED)
