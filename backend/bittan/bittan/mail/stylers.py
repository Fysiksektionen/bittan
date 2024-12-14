from datetime import datetime
from .mail import send_mail, MailImage, MailError
from ..models.payment import Payment
from ..models.chapter_event import ChapterEvent
from ..models.ticket import Ticket
from ..models.ticket_type import TicketType
import qrcode
import aggdraw
import io
import logging

def mail_ticket(payment: Payment):
    """
    Wrapper function to handle everything involved in sending an email containing the tickets in a payment.
    All tickets related to this payment must be from the same ChapterEvent.

	Raises:
		InvalidRecieverAddressError: Raised if reciever_address is not a valid email address.
		MailError: Raised if some miscellaneous error occured while sending the email.
    """
    ## Grab data ##
    tickets: list[Ticket] = list(payment.ticket_set.all()) # TODO order tickets by ticket_type for niceness
    if len(tickets) == 0:
        raise MailError("No tickets found associated with payment.")
    
    plural = len(tickets) > 1
    ticket_types: list[TicketType] = [ticket.ticket_type for ticket in tickets]
    chapter_event: ChapterEvent = tickets[0].chapter_event # We assume that all tickets are from the same ChapterEvent
    event_at: datetime = chapter_event.event_at
    date_string = f"{event_at.day}/{event_at.month} {event_at.year}"
    date_string_no_year = f"{event_at.day}/{event_at.month}"

    ## Generate message ##
    message = \
f"""
<html>
<h1>Din Fysikalenbiljett är här!</h1>

<img src="https://fysikalen.se/wordpress/wp-content/uploads/2024/07/LOGGA.png" alt="" width=300>

<p><b>Datum</b>: {date_string}</p>
<p><b>Dörrarna öppnas</b>: 18:00</p>
<p><b>Föreställningen börjar</b>: 19:00</p>
<p><b>Plats</b>: Kulturhuset Dieselverkstaden, Marcusplatsen 17, 131 54 Nacka. <i>Fri placering under föreställningen!</i></p>
"""
    if plural:
        message += f"<p>Du har köpt följande {len(tickets)} biljetter. Dessa finns även bifogade i detta mail.</p>"
    else:
        message += "<p>Du har köpt följande biljett. Denna finns även bifogad i detta mail.</p>"
    for ticket, ticket_type in zip(tickets, ticket_types):
        message += f'<img src="cid:biljett_{ticket.external_id}_embed" alt="{ticket_type.title} {date_string_no_year}: {ticket.external_id}">'
    
    message += \
"""
<p>Varmt välkommen!</p>

<p><u>Kvitto</u>:</p>
<p>[KVITTO... DETTA MAIL ÄR ETT TESTUTSKICK, EJ RIKTIG BILJETT]</p>

<i>Har du frågor angående ditt köp? Kontakta <a href="mailto:biljettsupport@f.kth.se">biljettsupport@f.kth.se</a>!</i>
</html>
"""

    ## Generate qr codes ##
    images_to_attach = []
    images_to_embed = []
    for ticket, ticket_type in zip(tickets, ticket_types):
        imagebytes = make_qr_image(text_qr=ticket.external_id, title=f"{ticket_type.title} {date_string_no_year}")
        images_to_attach.append(MailImage(imagebytes=imagebytes, filename=f"biljett_{ticket.external_id}"))
        images_to_embed.append(MailImage(imagebytes=imagebytes, filename=f"biljett_{ticket.external_id}_embed"))

    ## Send mail ##
    send_mail(reciever_address=payment.email, subject=f"Biljett, Fysikalen {date_string}", images_to_attach=images_to_attach, images_to_embed=images_to_embed, message_content=message)
    payment.sent_email = True
    payment.save()

def make_qr_image(text_qr: str, title: str) -> bytes:
	"""
	Creates a QR image. Meant to be used in a `MailImage` as `MailImage(make_qr_image(...), ...)`.

	Args:
		text_qr (str): Text to be encoded in the QR code.
		title (str): Text to be displayed above the QR code.

	Returns:
		bytes: A bytes representation of the image, encoded as png.
	"""

	TITLE_OFFSET = 10 # Offset relative to top of image
	TEXT_BOTTOM_OFFSET = 10 # Offset relative to bottom of image

	img = qrcode.make(text_qr)
	img = img.convert("RGBA")
	img_width, img_height = img.size 

	draw = aggdraw.Draw(img)
	font = aggdraw.Font("black", "/bittan/bittan/mail/OpenSans-Regular.ttf", 20)

	title_width = draw.textsize(title, font)[0]
	draw.text((((img_width-title_width)/2, TITLE_OFFSET)), title, font)

	text_bottom_width, text_bottom_height = draw.textsize(text_qr, font)
	draw.text((((img_width-text_bottom_width)/2, img_height-text_bottom_height-TEXT_BOTTOM_OFFSET)), text_qr, font)

	draw.flush()
	b = io.BytesIO()
	img.save(b, format="PNG")
	return b.getvalue()
 