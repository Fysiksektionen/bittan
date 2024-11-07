from bittan.services.swish.swish_payment_request import SwishPaymentRequest, PaymentStatus

def example_callback_handler_function(paymentRequest: SwishPaymentRequest):
	""" 
	An example of how the rest of the app can use the "swish-module". 
	The callback handler should be specified when initializing, the "Swish" class. 
	
	This callback is called whenever a payment status changes, e.g succeeds or is cancelled.
	"""
	print("~~EXAMPLE CALLBACK HANDLER~~")
	print("Payment status: ", paymentRequest.status)

	if paymentRequest.is_payed():
		print(f'Marking {paymentRequest.id} as paid')
	elif paymentRequest.status == PaymentStatus.CANCELLED.value:
		print(f'Payment {paymentRequest.id} failed because: {paymentRequest.status}')
	elif paymentRequest.status == PaymentStatus.CREATED.value:
		print(f'Payment {paymentRequest.id} is waiting...')
	elif paymentRequest.status == PaymentStatus.ROGUE.value:
		print(f'This needs to be handled cearefully.')
