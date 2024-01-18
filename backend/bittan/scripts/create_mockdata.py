#!/usr/bin/env python3

import os, sys

sys.path.append("..")
os.environ['DJANGO_SETTINGS_MODULE'] = "bittan.settings"
import django
django.setup()

from django.contrib.auth.models import User
from bittan.models import TicketType, ChapterEvent, ticket_type, Payment, Ticket
from bittan.models.payment import PaymentStatus
from bittan.models.ticket import TicketStatus
import datetime

User.objects.create_superuser("admin", None, "admin")
User.objects.create_user("staff", None, "staff", is_staff=True)

NOW = datetime.datetime.now()

standardbiljett = TicketType.objects.create(price=199.99, title="Standardbiljett", description="En vanlig biljett.")
studentbiljett = TicketType.objects.create(price=99.50, title="Studentbiljett", description="En billigare biljett.")

chapter_event1 = ChapterEvent.objects.create(title="Fysikalen Dag 1", description="Första dagen av Fysikalen.", max_tickets=10, sales_stop_at=NOW+datetime.timedelta(days=365))
chapter_event1.ticket_types.add(standardbiljett, studentbiljett)

payment1 = Payment.objects.create(
            time_created = NOW,
            swish_id = "Hej",
            status = PaymentStatus.ALIVE,
            telephone_number = "123-456 78 90",
            email = "mail@mail.com",
            total_price = 199.99,
            sent_email = True
        )

ticket1 = Ticket.objects.create(
            external_id = "1234",
            time_created = NOW,
            payment = payment1,
            status = TicketStatus.PAID,
            ticket_type = standardbiljett
        )
ChapterEvent(title="Fysikalen Dag 1").save()
