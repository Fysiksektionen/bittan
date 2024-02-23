import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class MailError(Exception):
	"""Base class for all Exceptions raised by mail."""
	pass

class InvalidRecieverAddressError(MailError):
	pass

def send_mail(reciever_address: str, subject: str, message_content: str):
	"""Sends a mail message. Only mails a single str with no attachments."""
	creds = _get_credentials()
	service = build("gmail", "v1", credentials=creds)
	message = EmailMessage()

	message.set_content(message_content)
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
	return

def _get_credentials() -> Credentials:
	scopes = ["https://www.googleapis.com/auth/gmail.send"]

	creds = None
	
	if os.path.exists("gmail_token.json"):
		creds = Credentials.from_authorized_user_file("gmail_token.json", scopes)
	if creds and creds.expired and creds.refresh_token:
		creds.refresh(Request())
		with open("gmail_token.json", "w") as f:
			f.write(creds.to_json())

	if not creds:
		raise Exception("Could not get Google Credentials")
	
	return creds
