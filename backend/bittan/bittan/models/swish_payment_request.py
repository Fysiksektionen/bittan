from django.db import models
from djmoney.models.fields import MoneyField
from django_enumfield import enum

class PaymentStatus(enum.Enum):
	PAID = 1,
	CANCELLED = 2
	WAITING = 3

class PaymentErrorCode(enum.Enum):
	TIMEOUT = 1
	CANCELLED_BY_USER = 2
	CANCELLED_OTHER = 3
	ERROR = 4
	FAILED_TO_INITIATE = 5

	
	__SWISH_ERROR_CODE_MAPPINGS = {
		"RF07": CANCELLED_OTHER,
		"BANKIDCL": CANCELLED_BY_USER,
		"FF10": ERROR,
		"TM01": TIMEOUT,

		"DS24": ERROR,  # SE TILL ATT DETTA HANTERAS SPECIELLT

		"VR01": ERROR,
		"VR02": ERROR,
	}

	@staticmethod
	def from_swish_reponse_code(status: str):
		return PaymentErrorCode.__SWISH_ERROR_CODE_MAPPINGS[status]


class SwishPaymentRequestModel(models.Model):
	# time_created = models.DateTimeField(auto_now_add=True)
	id = models.TextField(primary_key=True)
	status = enum.EnumField(PaymentStatus, default=PaymentStatus.WAITING)
	errorCode = enum.EnumField(PaymentErrorCode, null=True)

	amount = models.IntegerField()

	external_uri= models.TextField(null=True)

	swish_token = models.TextField(null=True)
	swish_request_data = models.TextField(null=True)
	
	def fail(self, fail_reason: PaymentErrorCode):
			self.status = PaymentStatus.CANCELLED
			self.errorCode = fail_reason