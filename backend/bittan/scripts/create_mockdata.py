#!/usr/bin/env python3

import os, sys

sys.path.append("..")
os.environ["DJANGO_SETTINGS_MODULE"] = "bittan.settings"
import django

django.setup()

from django.contrib.auth.models import User
from bittan.models import TicketType, ChapterEvent, Payment, Ticket, chapter_event
from bittan.models.payment import PaymentMethod, PaymentStatus
import datetime

User.objects.create_superuser("admin", None, "admin")
User.objects.create_user("staff", None, "staff", is_staff=True)

NOW = datetime.datetime.now()

bittanmarke = TicketType.objects.create(
	price=25,
	title="Bittanmärke",
	description="Ett märke väldigt fint märke. Du köper det nu och får en biljett för att hämta ut märket i kons!",
)

chapter_event1 = ChapterEvent.objects.create(
	title="Bittanmärke",
	description="Ett märke väldigt fint märke. Du köper det nu och får en biljett som du kan använda för att hämta ut ditt märke i kons!",
	total_seats=80,
	sales_stop_at=NOW + datetime.timedelta(days=365),
	event_at=NOW + datetime.timedelta(days=365),
)
chapter_event1.ticket_types.add(bittanmarke)


# payment1 = Payment.objects.create(
#             expires_at = NOW + datetime.timedelta(hours=1),
#             swish_id = "Hej",
#             status = PaymentStatus.RESERVED,
#             email = "mail@mail.com",
#             sent_email = False,
#             payment_method = PaymentMethod.SWISH,
#         )
#
# ticket1 = Ticket.objects.create(
#             external_id = "1234",
#             time_created = NOW,
#             payment = payment1,
#             ticket_type = standardbiljett,
#             chapter_event = chapter_event1
#         )
#
# chapter_event2 = ChapterEvent.objects.create(title="Fysikalen Dag 2", description="Andra dagen av Fysikalen.", total_seats=10, sales_stop_at=NOW+datetime.timedelta(days=365), event_at=NOW+datetime.timedelta(days=366))
# chapter_event2.ticket_types.add(standardbiljett, studentbiljett)
