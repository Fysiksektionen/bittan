#!/usr/bin/env python3

import os, sys

sys.path.append("..")
os.environ['DJANGO_SETTINGS_MODULE'] = "bittan.settings"
import django
django.setup()

from django.contrib.auth.models import User
from bittan.models import TicketType, ChapterEvent, Payment, Ticket, chapter_event
from bittan.models.payment import PaymentMethod, PaymentStatus
import datetime

User.objects.create_superuser("admin", None, "admin")
User.objects.create_user("staff", None, "staff", is_staff=True)

NOW = datetime.datetime.now()

studentbiljett = TicketType.objects.create(price=200, title="Studentbiljett", description="En vanlig biljett.", is_visible=False)
gratisbiljett = TicketType.objects.create(price=100, title="Gratisbiljett", description="En billigare biljett.", is_visible=False)
standardbiljett = TicketType.objects.create(price=100, title="Standardbiljett", description="En billigare biljett.", is_visible=False)
spexialbiljett = TicketType.objects.create(price=100, title="spexialbiljett", description="En billigare biljett.", is_visible=False)

chapter_event1 = ChapterEvent.objects.create(title="Fysikalen 2025: Earheart - 13/4 kl. 18 - Sön", description="Första dagen av Fysikalen.", total_seats=10, sales_stop_at=NOW+datetime.timedelta(days=365), event_at=NOW+datetime.timedelta(days=365))
chapter_event2 = ChapterEvent.objects.create(title="Fysikalen 2025: Earheart - 14/4 kl. 19 - Mån", description="Första dagen av Fysikalen.", total_seats=10, sales_stop_at=NOW+datetime.timedelta(days=365), event_at=NOW+datetime.timedelta(days=365))
chapter_event3 = ChapterEvent.objects.create(title="Fysikalen 2025: Earheart - 15/4 kl. 19 - Tis", description="Första dagen av Fysikalen.", total_seats=10, sales_stop_at=NOW+datetime.timedelta(days=365), event_at=NOW+datetime.timedelta(days=365))
chapter_event4 = ChapterEvent.objects.create(title="Fysikalen 2025: Earheart - 16/4 kl. 19 - Ons", description="Första dagen av Fysikalen.", total_seats=10, sales_stop_at=NOW+datetime.timedelta(days=365), event_at=NOW+datetime.timedelta(days=365))
chapter_event1.ticket_types.add(standardbiljett, studentbiljett, gratisbiljett, spexialbiljett)
chapter_event2.ticket_types.add(standardbiljett, studentbiljett, gratisbiljett, spexialbiljett)
chapter_event3.ticket_types.add(standardbiljett, studentbiljett, gratisbiljett, spexialbiljett)
chapter_event4.ticket_types.add(standardbiljett, studentbiljett, gratisbiljett, spexialbiljett)

