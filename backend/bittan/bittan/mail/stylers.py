from datetime import datetime
from .mail import send_mail, MailImage, MailError
from ..models.payment import Payment
from ..models.chapter_event import ChapterEvent
from ..models.ticket import Ticket
from ..models.ticket_type import TicketType
from django.utils import timezone
from django.db.models import Count, F
import qrcode
import aggdraw
import io
import logging
import os

def mail_payment(payment: Payment, send_receipt=True):
    """
    Wrapper function to handle everything involved in sending an email containing the tickets in a payment.
    All tickets related to this payment must be from the same ChapterEvent.

	Raises:
		InvalidReceiverAddressError: Raised if receiver_address is not a valid email address.
		MailError: Raised if some miscellaneous error occured while sending the email.
    """
    ## Grab data ##
    tickets: list[Ticket] = list(payment.ticket_set.order_by("ticket_type__title"))
    if len(tickets) == 0:
        raise MailError("No tickets found associated with payment.")
    
    plural = len(tickets) > 1
    ticket_types: list[TicketType] = [ticket.ticket_type for ticket in tickets]
    chapter_event: ChapterEvent = tickets[0].chapter_event # We assume that all tickets are from the same ChapterEvent
    event_at: datetime = timezone.localtime(chapter_event.event_at)
    doors_open: datetime = timezone.localtime(chapter_event.event_at - chapter_event.door_open_before)
    date_string = f"{event_at.day}/{event_at.month} {event_at.year}"
    date_string_no_year = f"{event_at.day}/{event_at.month}"
    start_time = event_at.strftime("%H:%M")
    doors_open = doors_open.strftime("%H:%M")

    paid_at = timezone.localtime(payment.time_paid)

    ## Generate message ##
    message = \
f"""
<html>
<h1>Din Fysikalenbiljett är här!</h1>

<img src="https://fysikalen.se/wordpress/wp-content/uploads/2024/07/LOGGA.png" alt="" width=300>

<p><b>Datum</b>: {date_string}</p>
<p><b>Dörrarna öppnas</b>: {doors_open}</p>
<p><b>Föreställningen börjar</b>: {start_time}</p>
<p><b>Plats</b>: Kulturhuset Dieselverkstaden, Marcusplatsen 17, 131 54 Nacka. </p>
<p><b>Speltid:</b> Ca. 3 timmar, inkl två pauser
<p><i>Observera att det är fri placering under föreställningen!</i></p>

<div style="border: 2px solid black; padding: 8px">
<b>Praktisk information</b>
<ul>
<li>Kollektivtrafik (buss och tvärbana) och parkering finns i anslutning till teatern.</li>
<li>Fika, programblad och märken finns att köpa innan föreställningen och i pauserna.</li>
<li>Toaletter finns på markplan och plan 2.</li>
<li>Gåvor till spexare kan lämnas på ett bord utanför ingången. Skriv mottagarens namn på gåvan så delar vi ut den på scen!</li>
</ul>

</div>

"""
    if plural:
        message += f"<p>Du har köpt följande {len(tickets)} biljetter. Dessa finns även bifogade i detta mail.</p>"
    else:
        message += "<p>Du har köpt följande biljett. Denna finns även bifogad i detta mail.</p>"
    for ticket, ticket_type in zip(tickets, ticket_types):
        message += f'<img src="cid:biljett_{ticket.external_id}_embed" alt="{ticket_type.title} {date_string_no_year}: {ticket.external_id}">'
    
    if send_receipt: 
        message += \
f"""
<p><u>Kvitto</u>:</p>
"""
    else: 
        message += \
f"""
<p><u>Orderöversikt</u>:</p>
"""
    message += \
f"""
<p><b>Referensnummer: </b>{payment.swish_id}</p>

<table style="border-spacing: 8px">
<tr>
<th align="left">Namn</th>
<th align="left">Antal</th>
<th align="left">á pris</th>
<th align="left">Moms</th>
<th align="left">Totalt</th>
</tr>

<p>Länk till <a href="https://drive.google.com/file/d/1biyd25AMdVJPcGlvS7PUojpc-Lj2jfDV/view?usp=drive_link">Köp- och leveransvillkor</a>
"""
    ticket_groups = (payment.ticket_set
        .values("ticket_type__title")
        .annotate(count=Count("id"))
        .annotate(price=F("ticket_type__price"))
    )
    for ticket_data in ticket_groups:
        message += \
f"""
<tr>
<td align="left">{chapter_event.title}: {ticket_data["ticket_type__title"]}</td>
<td align="left">{ticket_data["count"]}</td>
<td align="left">{ticket_data["price"]} kr</td>
<td align="left">{0*ticket_data["price"]} kr</td>
<td align="left">{ticket_data["count"]*ticket_data["price"]} kr</td>
<tr/>
"""

    message += \
f"""
<tr>
<td align="left">Summa</td>
<td></td>
<td></td>
<td>0 kr</td>
<td align="left">{sum(group["count"]*group["price"] for group in ticket_groups)} kr</td>
</tr>
</table>

<table style="border-spacing: 8px">
<tr>
<th align="left">Betalmetod</th>
<th align="left">Tid</th>
<tr/>

<tr>
<td align="left">{payment.payment_method}</td>
<td align="left">{paid_at.strftime("%Y-%m-%d")}</td>
</tr>
<tr>
<td></td>
<td align="left">{paid_at.strftime("%H:%M:%S")}</td>
</tr>
</tr>
</table>


<p>Fysiksektionen, THS <br/>
Brinellvägen 89 <br/>
100 44 Stockholm <br/>
Momsnummer: SE802411-894801</p>
"""

    message += \
"""
<p><b>Vi ser fram emot att få spexa för dig!</b></p>
<p><i>Har du frågor angående ditt köp? Kontakta <a href="mailto:biljettsupport@f.kth.se">biljettsupport@f.kth.se</a>!</i></p>
<p><i>Nyfiken på Fyskalen? Du kan läsa mer om oss på <a href="https://fysikalen.se">fysikalen.se</a>.</i></p>
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
    send_mail(receiver_address=payment.email, subject=f"Biljett: {chapter_event.title}", images_to_attach=images_to_attach, images_to_embed=images_to_embed, message_content=message)
    payment.sent_email = True
    payment.save()

def mail_bittan_developers(message_content: str, subject: str = ""):
    """
    Sends a mail to the developers of bittan. Use in case of unexpected errors!

	Args:
		message_content (str): The text sent in the email. Should contain details of the error.
		subject (str): A short summary of the error to be appended to the subject of the email (optional).

	Raises:
		MailError: Raised if some miscellaneous error occurred while sending the email.
    """

    full_subject = "BACKEND ERROR"
    if subject:
        full_subject += f": {subject}" 

    NOW = timezone.localtime(timezone.now())
    full_message = f"This is an automated mail sent by BitTan because an error has occurred at {NOW}. The following information has been attached:\n\n" + message_content
    send_mail(receiver_address="biljettsupport@f.kth.se", subject=full_subject, message_content=full_message, format_as_html=False)

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
	font = aggdraw.Font("black", os.path.join(os.path.dirname(__file__), "OpenSans-Regular.ttf"), 20)

	title_width = draw.textsize(title, font)[0]
	draw.text((((img_width-title_width)/2, TITLE_OFFSET)), title, font)

	text_bottom_width, text_bottom_height = draw.textsize(text_qr, font)
	draw.text((((img_width-text_bottom_width)/2, img_height-text_bottom_height-TEXT_BOTTOM_OFFSET)), text_qr, font)

	draw.flush()
	b = io.BytesIO()
	img.save(b, format="PNG")
	return b.getvalue()
 
