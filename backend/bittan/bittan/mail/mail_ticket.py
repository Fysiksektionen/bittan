from .mail import send_mail, make_qr_image

def mail_ticket(reciever_address: str):
    """"Wrapper function to handle everything involved in sending an email containing a ticket."""
    message = "Testmeddelande"
    send_mail(reciever_address=reciever_address, subject="Test-subject", message_content=message)
