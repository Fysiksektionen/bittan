from enum import Enum

from bittan.models.swish_payment_request import SwishPaymentRequestModel, PaymentErrorCode as SwishApiPaymentErrorCode, PaymentStatus as SwishApiStatus 

"""
This file contains all of the user-facing data structures
"""

class PaymentStatus(Enum):
	PAID = 1,
	CANCELLED = 2
	# WAITING = 3

	__SWISH_API_STATUS_MAPPINGS = {
		# TODO Fill in the types when swish docs are updated
		SwishApiStatus.CANCELLED: CANCELLED,
		# SwishApiStatus.WAITING: WAITING,
		SwishApiStatus.PAID: PAID,
	}

	@staticmethod
	def __from_swish_api_status(status: SwishApiStatus):
		return PaymentStatus.__SWISH_API_STATUS_MAPPINGS[status] 

class PaymentErrorCode(Enum):
	TIMEOUT = 1
	CANCELLED_BY_USER = 2
	CANCELLED_OTHER = 3
	FAILED_TO_INITIATE = 5

	
	__SWISH_ERROR_CODE_MAPPINGS = {
		# TODO Fill in the types when swish docs are updated
		SwishApiPaymentErrorCode.FAILED_TO_INITIATE: FAILED_TO_INITIATE,
		SwishApiPaymentErrorCode.UNKNOWN: CANCELLED_OTHER,
	}

	@staticmethod
	def __from_swish_api_error(status: SwishApiPaymentErrorCode):
		return PaymentErrorCode.__SWISH_ERROR_CODE_MAPPINGS[status]

class SwishPaymentRequest:
	"""A class that represents all the user of this api needs to know about a payment"""
	def __init__(self, paymentRequest: SwishPaymentRequestModel):
		self.id = paymentRequest.id
		self.status = PaymentStatus.__from_swish_api_status(paymentRequest.status)
		self.errorCode = PaymentErrorCode.__from_swish_api_error(paymentRequest.error_code)
		self.token = paymentRequest.token or None
		self.amount = paymentRequest.amount
		
	def is_payed(self):
		return self.status == PaymentStatus.PAID
	
	id: str
	amount: int

	status: PaymentStatus 
	errorCode: PaymentErrorCode | None

	# Used to start the swish app. Used by the frontent to make the payment
	token: str | None