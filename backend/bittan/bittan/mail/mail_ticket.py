from .mail import send_mail, make_qr_image, MailImage

def mail_ticket(reciever_address: str):
    """"Wrapper function to handle everything involved in sending an email containing a ticket."""
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
