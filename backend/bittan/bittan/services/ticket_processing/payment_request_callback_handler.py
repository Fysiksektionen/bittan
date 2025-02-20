from bittan.services.swish.swish import payment_signal 
from django.dispatch import receiver
from bittan.models.payment import Payment, PaymentStatus

from bittan.mail import mail_payment


def payment_request_callback_handler(sender, **kwargs):
	payment_request = kwargs["payment_request"]

	payment = Payment.objects.get(swish_id=payment_request.id) 
	if payment_request.is_paid(): 
		payment.status = PaymentStatus.PAID 
		# TODO handle errors
		mail_payment(payment)


	if payment_request.is_failed():
		payment.status = PaymentStatus.FAILED_EXPIRED_RESERVATION
	payment.save()
