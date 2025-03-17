import logging
from bittan.mail.mail import MailError
from bittan.mail.stylers import mail_bittan_developers
from bittan.models.payment import Payment, PaymentStatus

from bittan.mail import mail_payment


def payment_request_callback_handler(sender, **kwargs):
	payment_request = kwargs["payment_request"]
	logging.info(f"Received callback from Swish for SwishId: {payment_request.id}")
	payment = Payment.objects.get(swish_id=payment_request.id)
	
	if payment_request.is_paid():
		payment.status = PaymentStatus.PAID
		payment.time_paid = payment_request.date_paid
		payment.save()
		logging.info(f"Payment id: {payment.pk}; Swish id: {payment.swish_id} marked as paid in callback.")
		# Ugly hack to make the string into a datetime object
		payment = Payment.objects.get(swish_id=payment_request.id)

		try:
			mail_payment(payment)
		except MailError as e:
			# TODO mail staff?
			logging.warning(
				f'Unable to send mail of payment {payment.pk} due to a mail error: {e}'
			)
		except Exception as e:
			logging.warning(f'Unable to send mail of payment {payment.pk}, {e}')

		try:
			mail_bittan_developers(f"Could not send payment confirmation mail: payment primary key: {payment.pk}, Error {e}", "Could not send confirmation mail!")
		except Exception as e:
			pass


	if payment_request.is_failed():
		logging.info(f"Payment id: {payment.pk}; Swish id: {payment.swish_id} marked as failed in callback.")
		payment.status = PaymentStatus.FAILED_EXPIRED_RESERVATION
	payment.save()
