from .mail import send_mail, make_qr_image

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

<p>Du har köpt 3 biljetter som finns bifogade i detta mail.
Om de inte fungerar, använd följande koder:</p>
<ul>
    <li>Biljett 1: <code>ABCDEF</code> (Studentbiljett)</li>
    <li>Biljett 2: <code>GHIJKL</code> (Standardbiljett)</li>
    <li>Biljett 3: <code>MNOPQR</code> (Standardbiljett)</li>
</ul>
<img src="cid:biljett_ABCDEF" alt="Biljettkod ABCDEF">

<p><u>Kvitto</u>:</p>
<p>[KVITTO... DETTA MAIL ÄR ETT TESTUTSKICK, EJ RIKTIG BILJETT]</p>

<i>Har du frågor angående ditt köp, eller vill begära återbetalning? Kontakta <a href="mailto:biljettsupport@f.kth.se">biljettsupport@f.kth.se</a>!</i>
</html>
"""
    attachment1 = make_qr_image(content="ABCDEF")
    send_mail(reciever_address=reciever_address, subject="Biljett, Fysikalen 1/1 2024", image=attachment1, image_filename="biljett_ABCDEF", message_content=message)
