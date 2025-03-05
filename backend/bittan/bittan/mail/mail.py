import os
import logging
from dataclasses import dataclass
from typing import List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import base64
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class MailError(Exception):
	"""Base class for all Exceptions raised by mail."""
	pass

class InvalidReceiverAddressError(MailError):
	pass

@dataclass
class MailImage:
	"""An image to be attached or embedded in a mail."""
	imagebytes: bytes
	filename: str
	"The desired filename without any extension (no .png)"

def send_mail(receiver_address: str, subject: str, message_content: str, images_to_attach: list[MailImage] = [], images_to_embed: list[MailImage] = [], format_as_html: bool = True):
	"""
	Sends an email message.

	Args:
		receiver_address (str): The email address that should receive the email.
		subject (str): The subject of the email.
		message_content (str): The text sent in the email.
		images_to_attach (list[MailImage]): A list of `MailImage`s to attach. Assumes png formatting. Defaults to an empty list.
		images_to_embed (list[MailImage]): A list of `MailImage`s to embed. Their `Content-Id` will be set to the `filename` attributes. Assumes png formatting. Defaults to an empty list.
		format_as_html (bool): Whether the `message_content` should be interpreted as html. Defaults to `True`.

	Raises:
		InvalidReceiverAddressError: Raised if receiver_address is not a valid email address.
		MailError: Raised if some miscellaneous error occurred while sending the email.
	"""
	creds = _get_credentials()
	service = build("gmail", "v1", credentials=creds)

	message = MIMEMultipart("related")
	message["Subject"] = subject
	message["To"] = receiver_address
	message.attach(MIMEText(message_content, ("html" if format_as_html else "plain")))

	for image_to_embed in images_to_embed:
		img = MIMEImage(image_to_embed.imagebytes, name=f"{image_to_embed.filename}.png")
		img.add_header("Content-ID", f"<{image_to_embed.filename}>")
		img.add_header("Content-Disposition", "inline", filename=f"{image_to_embed.filename}.png")
		message.attach(img)
	for image_to_attach in images_to_attach:
		img = MIMEImage(image_to_attach.imagebytes, name=f"{image_to_attach.filename}.png")
		img.add_header("Content-Disposition", "attachment", filename=f"{image_to_attach.filename}.png")
		message.attach(img)
	
	encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
	create_message = {"raw": encoded_message}

	try:
		sent_message = (
			service.users()
			.messages()
			.send(userId="me", body=create_message)
			.execute()
		)
	except HttpError as error:
		if error.reason == "Invalid To header":
			raise InvalidReceiverAddressError(f"Invalid address: '{receiver_address}'")
	if not "SENT" in sent_message["labelIds"]:
		logging.error(f"Could not send mail. Address: {receiver_address}; Has image: {bool(image)}; Message content:\n{message_content}")
		raise MailError("Mail was not sent for unknown reasons.")
	return

def send_bulk_mail(receiver_addresses: List[str], subject: str, message_content: str, format_as_html: bool=True) -> None:
	"""
	Sends an email message to multiple receivers in bulk.

	Args:
		receiver_addresses (List[str]): List of email addresses that should receive the email.
		subject (str): The subject of the email.
		message_content (str): The text sent in the email.
		format_as_html (bool): Whether the `message_content` should be interpreted as html. Defaults to `True`.

	Raises:
		InvalidReceiverAddressError: Raised if receiver_address is not a valid email address.
		MailError: Raised if some miscellaneous error occurred while sending the email.
	"""
	creds = _get_credentials()
	service = build("gmail", "v1", credentials=creds)
	
	for receiver_address in receiver_addresses:
		message = MIMEMultipart("related")
		message["Subject"] = subject
		message.attach(MIMEText(message_content, ("html" if format_as_html else "plain")))
		message["To"] = receiver_address
		
		encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
		create_message = {"raw": encoded_message}

		try:
			sent_message = (
				service.users()
				.messages()
				.send(userId="me", body=create_message)
				.execute()
			)
		except HttpError as error:
			if error.reason == "Invalid To header":
				raise InvalidReceiverAddressError(f"Invalid address: '{receiver_address}'")
		if not "SENT" in sent_message["labelIds"]:
			logging.error(f"Could not send mail. Address: {receiver_address}; Has image: {bool(image)}; Message content:\n{message_content}")
			raise MailError("Mail was not sent for unknown reasons.")

	return

def _get_credentials() -> Credentials:
	scopes = ["https://www.googleapis.com/auth/gmail.send"]

	creds = None
	
	if os.path.exists("gmail_token.json"):
		creds = Credentials.from_authorized_user_file("gmail_token.json", scopes)
	if creds and creds.expired and creds.refresh_token:
		try:
			creds.refresh(Request())
		except RefreshError as e:
			logging.error(f"Could not get Google Credentials because Refresh failed, causing the following exception:\n{e}")
			raise MailError("Could not get Google Credientials")
		with open("gmail_token.json", "w") as f:
			f.write(creds.to_json())

	if not creds:
		logging.error("Could not get Google Credentials, unknown reason.")
		raise MailError("Could not get Google Credentials")
	
	return creds
