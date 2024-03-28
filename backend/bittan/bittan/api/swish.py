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
	print(request.data)

	Swish.get_instance().handle_swish_callback(request.data)

	# Swish expects a 201 when a callback is sucessfully recieved
	return Response("", status=status.HTTP_201_CREATED)


@api_view(['POST'])
def debug_make_request(request: Request):
	resp = Swish.get_instance().create_swish_payment(123, "Hejsan")
	print("Skapade betalning")
	print(f'id: {resp.id}, token: {resp.token}')
	return Response(f"{resp.id}", status=status.HTTP_201_CREATED)

@api_view(['POST'])
def debug_query(request: Request, id):
	# print("KÖRDE DEBUG QUERY")
	resp = Swish.get_instance().get_payment_request(id)
	print(resp)
	print(f'id: {resp.id}, token?: {resp.token or ''}, status: {resp.status}')
	return Response("Letade lite i databasen", status=status.HTTP_200_OK)