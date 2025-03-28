from django.db import models
from django_enumfield import enum
import logging

from bittan.mail.stylers import mail_bittan_developers

class PaymentStatus(enum.Enum):
	# Seems to be duplicate of transaction declined, either here or in PaymentErrorCode. See https://github.com/Fysiksektionen/bittan/issues/13
	""" Swish-side status of a payment """
	PAID = 1
	CANCELLED = 2 
	CREATED = 3
	DECLINED = 4
	ERROR = 5

	__SWISH_API_STATUS_MAPPINGS = {
		"PAID": PAID,
		"CANCELLED": CANCELLED,
		"CREATED":CREATED,
		"DECLINED": DECLINED,
		"ERROR": ERROR,
	}

	@staticmethod
	def from_swish_api_status(status: str):
		""" Try to get the status from the mapping otherwise log an error and None """
		if status not in PaymentStatus.__SWISH_API_STATUS_MAPPINGS:
			logging.critical(f"Unknown Swish API status: {status}")
			try:
				mail_bittan_developers(f"Swish sent the status {status}, but this status string is not known, or handled by our code.", "Unknown swish response status")
			except Exception as _:
				pass

			return None
		return PaymentStatus[status]

class PaymentErrorCode(enum.Enum):
	UNKNOWN = 0
	FAILED_TO_INITIATE = 1

	TIMEOUT = 2
	CANCELLED = 3

	SWISH_HAS_NO_IDEA_WHAT_IS_HAPPENING = 4

	
	__SWISH_ERROR_CODE_MAPPINGS = {
		"RF07": CANCELLED,
		"BANKIDCL": CANCELLED,
		"TM01": TIMEOUT,

		"DS24": SWISH_HAS_NO_IDEA_WHAT_IS_HAPPENING,
	}

	@staticmethod
	def from_swish_reponse_code(status: str|None):
		if status is None:
			return None

		if status not in PaymentErrorCode.__SWISH_ERROR_CODE_MAPPINGS:
			logging.info(f"Swish sent an error code, '{status}', which is not in the swish error code mapping enum")
			return PaymentErrorCode.UNKNOWN
		return PaymentErrorCode.__SWISH_ERROR_CODE_MAPPINGS[status]

class SwishPaymentRequestModel(models.Model):
	time_created = models.DateTimeField(auto_now_add=True)
	id = models.TextField(primary_key=True)
	status = enum.EnumField(PaymentStatus, default=PaymentStatus.CREATED)
	error_code = enum.EnumField(PaymentErrorCode, null=True)

	date_paid = models.DateTimeField(null=True)

	amount = models.IntegerField()

	external_uri= models.TextField(null=True)

	token = models.TextField(null=True)

	swish_api_response = models.TextField(null=True)
	
	def fail(self, fail_reason: PaymentErrorCode):
			self.status = PaymentStatus.ERROR
			self.error_code = fail_reason
