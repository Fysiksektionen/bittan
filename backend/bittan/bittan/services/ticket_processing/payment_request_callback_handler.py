import logging
from bittan.mail.mail import MailError
from bittan.mail.stylers import mail_bittan_developers
from bittan.models.payment import Payment, PaymentStatus

from bittan.mail import mail_payment


def payment_request_callback_handler(sender, **kwargs):
	payment_request = kwargs["payment_request"]

	payment = Payment.objects.get(swish_id=payment_request.id)
	payment.status = PaymentStatus.PAID
	try:
		mail_payment(payment)
	except MailError as e:
		logging.warning(
			f'Unable to send mail of payment {payment.pk} due to a mail error: {e}'
		)

		try:
			mail_bittan_developers(f"Could not send payment confirmation mail: payment primary key: {payment.pk}, Error {e}", "Could not send confirmation mail!")
		except Exception as e:
			pass

	except Exception as e:
		logging.warning(f'Unable to send mail of payment {payment.pk}, {e}')

		try:
			mail_bittan_developers(f"Could not send payment confirmation mail: payment primary key: {payment.pk}, Error {e}", "Could not send confirmation mail!")
		except Exception as e:
			pass


	if payment_request.is_failed():
		payment.status = PaymentStatus.FAILED_EXPIRED_RESERVATION
	payment.save()
