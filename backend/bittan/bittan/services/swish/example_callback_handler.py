from bittan.services.swish.swish_payment_request import SwishPaymentRequest, PaymentStatus

def example_callback_handler_function(paymentRequest: SwishPaymentRequest):
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
