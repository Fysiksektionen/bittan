#!/usr/bin/env python3

import os, sys

sys.path.append("..")
os.environ['DJANGO_SETTINGS_MODULE'] = "bittan.settings"
import django
django.setup()

from django.contrib.auth.models import User
from bittan.models import TicketType, ChapterEvent, ticket_type, Payment, Ticket
from bittan.models.payment import PaymentStatus
import datetime

User.objects.create_superuser("admin", None, "admin")
User.objects.create_user("staff", None, "staff", is_staff=True)

NOW = datetime.datetime.now()

standardbiljett = TicketType.objects.create(price=200, title="Standardbiljett", description="En vanlig biljett.")
studentbiljett = TicketType.objects.create(price=100, title="Studentbiljett", description="En billigare biljett.")

chapter_event1 = ChapterEvent.objects.create(title="Fysikalen Dag 1", description="Första dagen av Fysikalen.", max_tickets=10, sales_stop_at=NOW+datetime.timedelta(days=365), event_at=NOW+datetime.timedelta(days=365))
chapter_event1.ticket_types.add(standardbiljett, studentbiljett)

chapter_event2 = ChapterEvent.objects.create(title="Fysikalen Dag 2", description="Andra dagen av Fysikalen.", max_tickets=10, sales_stop_at=NOW+datetime.timedelta(days=365), swish_message="Hej på dig du. ")


payment1 = Payment.objects.create(
            expires_at = NOW + datetime.timedelta(hours=1),
            swish_id = "Hej",
            status = PaymentStatus.RESERVED,
            email = "mail@mail.com",
            sent_email = True
        )

ticket1 = Ticket.objects.create(
            external_id = "1234",
            time_created = NOW,
            payment = payment1,
            ticket_type = standardbiljett
        )

chapter_event2 = ChapterEvent.objects.create(title="Fysikalen Dag 2", description="Andra dagen av Fysikalen.", max_tickets=10, sales_stop_at=NOW+datetime.timedelta(days=365), event_at=NOW+datetime.timedelta(days=366))
chapter_event2.ticket_types.add(standardbiljett, studentbiljett)
