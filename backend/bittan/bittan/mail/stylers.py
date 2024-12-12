from .mail import send_mail, make_qr_image, MailImage
import qrcode
import aggdraw
import io
import logging

def mail_ticket(reciever_address: str):
    """Wrapper function to handle everything involved in sending an email containing a ticket."""
    message = \
"""
<html>
<h1>Din Fysikalenbiljett är här!</h1>

<div class="center">
    <img src="https://fysikalen.se/wordpress/wp-content/uploads/2024/07/LOGGA.png" alt="" width=300>
</div>

<p><b>Tid</b>: 1/1 2024, 18:00.</p>
<p><b>Plats</b>: Kulturhuset Dieselverkstaden, Marcusplatsen 17, 131 54 Nacka. <i>Fri placering under föreställningen!</i></p>

<p>Du har köpt följande 3 biljetter. Dessa finns även bifogade i detta mail.</p>
<img src="cid:biljett_ABCDEF_embed" alt="Studentbiljett 1/1: ABCDEF">
<img src="cid:biljett_GHIJKL_embed" alt="Standardbiljett 1/1: GHIJKL">
<img src="cid:biljett_MNOPQR_embed" alt="Seniorbiljett 1/1: MNOPQR">

<p><u>Kvitto</u>:</p>
<p>[KVITTO... DETTA MAIL ÄR ETT TESTUTSKICK, EJ RIKTIG BILJETT]</p>

<i>Har du frågor angående ditt köp, eller vill begära återbetalning? Kontakta <a href="mailto:biljettsupport@f.kth.se">biljettsupport@f.kth.se</a>!</i>
</html>
"""
    qr_codes = ["ABCDEF", "GHIJKL", "MNOPQR"]
    titles = ["Studentbiljett 1/1", "Standardbiljett 1/1", "Seniorbiljett 1/1"]
    images_to_attach = []
    images_to_embed = []
    for qr_code, title in zip(qr_codes, titles):
        imagebytes = make_qr_image(text_qr=qr_code, title=title)
        images_to_attach.append(MailImage(imagebytes=imagebytes, filename=f"biljett_{qr_code}"))
        images_to_embed.append(MailImage(imagebytes=imagebytes, filename=f"biljett_{qr_code}_embed"))
    send_mail(reciever_address=reciever_address, subject="Biljett, Fysikalen 1/1 2024", images_to_attach=images_to_attach, images_to_embed=images_to_embed, message_content=message)

def make_qr_image(text_qr: str, title: str) -> bytes:
	"""
	Creates a QR image. Meant to be used together with `send_mail`, such as:
	```
	send_mail(..., image=make_qr_image("abc"), ...)
	```

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
 