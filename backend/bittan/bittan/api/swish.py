from rest_framework import status 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from ..services.swish import Swish
from ..models.swish_payment_request import PaymentStatus, PaymentErrorCode


class SwishCallbackRequest():
	status: PaymentStatus
	errorCode: PaymentErrorCode
	all_data_str: str 

	def __init__(self, data: dict):
		self.all_data_str = str(data)
		self.status = PaymentStatus.PAID
		self.errorCode = None

		if data.get('status') != 'PAID':
			self.status = PaymentStatus.CANCELLED
			self.errorCode = PaymentErrorCode.from_swish_reponse_code(data.get('errorCode'))


@api_view(['POST'])
def swish_callback(request: Request):
	print("Tog emot en request från swish:")
	swish_callback = SwishCallbackRequest(request.data)
	print(swish_callback)

	# reference = request.data.get("paymentReference")
	# response_code = PaymentResponseCode.from_swish_reponse_code(request.data.get('status'))
	# # if request.status
	# print(response_code)

	# Swish.get_instance().callback_function(reference, response_code)
	return Response("Hello :D", status=status.HTTP_201_CREATED)
