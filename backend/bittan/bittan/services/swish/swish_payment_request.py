from enum import Enum

from django.utils.log import logging

from bittan.models.swish_payment_request import SwishPaymentRequestModel, PaymentErrorCode as SwishApiPaymentErrorCode, PaymentStatus as SwishApiPaymentStatus 

"""
This file contains all of the user-facing data structures
"""

class PaymentStatus(Enum):
	PAID = 1,
	CANCELLED = 2
	CREATED = 3
	ERROR = 4

	# We have no idea what is happening
	ROGUE = 5

	__SWISH_API_STATUS_MAPPINGS = {
		# TODO Fill in the types when swish docs are updated
		SwishApiPaymentStatus.CANCELLED: CANCELLED,
		SwishApiPaymentStatus.DECLINED: CANCELLED,
		SwishApiPaymentStatus.CREATED: CREATED,
		SwishApiPaymentStatus.PAID: PAID,
		SwishApiPaymentStatus.ERROR: ERROR,
	}

	@staticmethod
	def from_swish_api_status(status: SwishApiPaymentStatus):
		if status not in PaymentStatus.__SWISH_API_STATUS_MAPPINGS:
			logging.warn(f'{status} does not have a corresponding map in PaymentStatus')
			return PaymentStatus.ROGUE

		return PaymentStatus.__SWISH_API_STATUS_MAPPINGS[status] 

class PaymentErrorCode(Enum):
	TIMEOUT = 1
	CANCELLED= 2
	FAILED_TO_INITIATE = 3
	UNKNOWN = 4
	FATAL_ERROR = 4
	
	__SWISH_ERROR_CODE_MAPPINGS = {
		# TODO Fill in the types when swish docs are updated
		SwishApiPaymentErrorCode.FAILED_TO_INITIATE: FAILED_TO_INITIATE,
		SwishApiPaymentErrorCode.UNKNOWN: UNKNOWN,
		SwishApiPaymentErrorCode.TIMEOUT: TIMEOUT,
		SwishApiPaymentErrorCode.CANCELLED: CANCELLED,
		SwishApiPaymentErrorCode.SWISH_HAS_NO_IDEA_WHAT_IS_HAPPENING: FATAL_ERROR,


	}

	@staticmethod
	def from_swish_api_error(status: SwishApiPaymentErrorCode | None):
		if status is None:
			return None

		if status not in PaymentErrorCode:
			logging.warn(f'{status} does not have a corresponding map in PaymentErrorCode')
			return PaymentErrorCode.UNKNOWN
			# logging.log("Should not happen")
		return PaymentErrorCode.__SWISH_ERROR_CODE_MAPPINGS[status]

class SwishPaymentRequest:
	"""A class that represents all the user of this api needs to know about a payment"""
	def __init__(self, paymentRequest: SwishPaymentRequestModel):
		self.id = paymentRequest.id
		self.status = PaymentStatus.from_swish_api_status(paymentRequest.status)
		self.errorCode = PaymentErrorCode.from_swish_api_error(paymentRequest.error_code)
		self.token = paymentRequest.token or None
		self.amount = paymentRequest.amount

		print(self.id)
		print(self.status)
		print(self.errorCode)
		print(self.token)
		print(self.amount)
		
	def is_payed(self):
		return self.status == PaymentStatus.PAID
	
	id: str
	amount: int

	status: PaymentStatus 
	errorCode: PaymentErrorCode | None

	# Used to start the swish app. Used by the frontent to make the payment
	token: str | None
