import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import qrcode
import io
import logging

class MailError(Exception):
	"""Base class for all Exceptions raised by mail."""
	pass

class InvalidRecieverAddressError(MailError):
	pass

def make_qr_image(content: str) -> bytes:
	"""
	Creates a QR image. Meant to be used together with `send_mail`, such as:
	```
	send_mail(..., image=make_qr_image("abc"), ...)
	```

	Args:
		content (str): The text to be encoded.

	Returns:
		bytes: A bytes representation of the image, encoded as png.
	"""
	img = qrcode.make(content)
	b = io.BytesIO()
	img.save(b, format="PNG")
	return b.getvalue()

def send_mail(reciever_address: str, subject: str, message_content: str, image: bytes | None = None, image_filename: str = "Biljett"):
	"""
	Sends an email message.

	Args:
		reciever_address (str): The email address that should recieve the email.
		subject (str): The subject of the email.
		message_content (str): The text sent in the email.
		image (bytes | None, optional): A png image to attach. Defaults to None.
		image_filename (str, optional): The filename of the image attachment. Only applied if image is not None. Defaults to "Biljett".

	Raises:
		InvalidRecieverAddressError: Raised if reciever_address is not a valid email address.
		MailError: Raised if some miscellaneous error occured while sending the email.
	"""
	creds = _get_credentials()
	service = build("gmail", "v1", credentials=creds)
	message = EmailMessage()

	message.set_content(message_content)
	if image is not None:
		message.add_attachment(image, maintype="image", subtype="png", filename=image_filename)
	message["To"] = reciever_address
	message["Subject"] = subject
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
			raise InvalidRecieverAddressError(f"Invalid address: '{reciever_address}'")
	if not "SENT" in sent_message["labelIds"]:
		logging.error(f"Could not send mail. Address: {reciever_address}; Message content:\n{message_content}")
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
