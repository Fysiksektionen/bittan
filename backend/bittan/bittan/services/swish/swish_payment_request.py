from enum import Enum

from django.utils.log import logging

from bittan.models.swish_payment_request import SwishPaymentRequestModel, PaymentErrorCode as SwishApiPaymentErrorCode, PaymentStatus as SwishApiPaymentStatus 

"""
This file contains all of the user-facing data structures
"""

class PaymentStatus(Enum):
	""" Status of a payment """
	PAID = 1,
	CANCELLED = 2
	CREATED = 3

	# ERRORS 
	TIMEOUT = 4
	FAILED_TO_INITIATE = 5
	UNKNOWN_ERROR = 6

	# We have no idea what is happening
	ROGUE = 7

	__SWISH_API_STATUS_MAPPINGS = {
		SwishApiPaymentStatus.CANCELLED: CANCELLED,
		SwishApiPaymentStatus.DECLINED: CANCELLED,
		SwishApiPaymentStatus.CREATED: CREATED,
		SwishApiPaymentStatus.PAID: PAID,
		# SwishApiPaymentStatus.ERROR must be handled separately since it has multiple possibilities
	}


	__SWISH_ERROR_CODE_MAPPINGS = {
		SwishApiPaymentErrorCode.FAILED_TO_INITIATE: FAILED_TO_INITIATE,
		SwishApiPaymentErrorCode.UNKNOWN: UNKNOWN_ERROR,
		SwishApiPaymentErrorCode.TIMEOUT: TIMEOUT,
		SwishApiPaymentErrorCode.CANCELLED: CANCELLED,
		SwishApiPaymentErrorCode.SWISH_HAS_NO_IDEA_WHAT_IS_HAPPENING: ROGUE,
	}

	@staticmethod
	def from_swish_api_error(error: SwishApiPaymentErrorCode):
		if error not in PaymentStatus.__SWISH_ERROR_CODE_MAPPINGS:
			logging.warn(f'{error} does not have a corresponding map in PaymentErrorCode')
			return PaymentStatus.UNKNOWN_ERROR
		return PaymentStatus.__SWISH_ERROR_CODE_MAPPINGS[error]

	@staticmethod
	def from_swish_api_status(status: SwishApiPaymentStatus, error_code: SwishApiPaymentErrorCode):
		""" Converts the Swish API:s error and status into a user facing status """
		if status == SwishApiPaymentStatus.ERROR:
			return PaymentStatus.from_swish_api_error(error_code)

		if status not in PaymentStatus.__SWISH_API_STATUS_MAPPINGS:
			logging.warn(f'{status} does not have a corresponding map in PaymentStatus')
			return PaymentStatus.ROGUE

		return PaymentStatus.__SWISH_API_STATUS_MAPPINGS[status] 



class SwishPaymentRequest:
	id: str
	amount: int
	status: PaymentStatus 

	# Used to start the swish app. Used by the frontent to make the payment
	token: str | None

	"""	A class that represents all the user of *this* api needs to know about a payment """
	def __init__(self, paymentRequest: SwishPaymentRequestModel):
		self.id = paymentRequest.id
		self.status = PaymentStatus.from_swish_api_status(paymentRequest.status, paymentRequest.error_code)
		self.token = paymentRequest.token or None
		self.amount = paymentRequest.amount

		print(self.id)
		print(self.status)
		print(self.token)
		print(self.amount)
		
	def is_payed(self):
		return self.status == PaymentStatus.PAID

	def is_failed(self):
		return self.status != PaymentStatus.PAID and self.status != PaymentStatus.CREATED
	
