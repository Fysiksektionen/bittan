from bittan.services.swish.swish_payment_request import SwishPaymentRequest, PaymentStatus
from bittan.services.swish.swish import payment_signal

def example_callback_handler_function(sender, **kwargs):
	""" 
	An example of how the rest of the app can use the "swish-module". 
	The callback handler should be specified when initializing, the "Swish" class. 
	
	This callback is called whenever a payment status changes, e.g succeeds or is cancelled.
	"""

	payment_request = kwargs["payment_request"]

	print("~~EXAMPLE CALLBACK HANDLER~~")
	print("Payment status: ", payment_request.status)

	if payment_request.is_paid():
		print(f'Marking {payment_request.id} as paid')
	elif payment_request.status == PaymentStatus.CANCELLED.value:
		print(f'Payment {payment_request.id} failed because: {payment_request.status}')
	elif payment_request.status == PaymentStatus.CREATED.value:
		print(f'Payment {payment_request.id} is waiting...')
	elif payment_request.status == PaymentStatus.ROGUE.value:
		print(f'This needs to be handled cearefully.')


