#!/usr/bin/env python3

import os, sys

sys.path.append("..")
os.environ['DJANGO_SETTINGS_MODULE'] = "bittan.settings"
import django
django.setup()

from django.contrib.auth.models import User
from bittan.models import TicketType, ChapterEvent
import datetime

User.objects.create_superuser("admin", None, "admin")

NOW = datetime.datetime.now()

standardbiljett = TicketType.objects.create(price=199.99, title="Standardbiljett", description="En vanlig biljett.")
studentbiljett = TicketType.objects.create(price=99.50, title="Studentbiljett", description="En billigare biljett.")

chapter_event1 = ChapterEvent.objects.create(title="Fysikalen Dag 1", description="Första dagen av Fysikalen.", max_tickets=10, sales_stop_at=NOW+datetime.timedelta(days=365))
chapter_event1.ticket_types.add(standardbiljett, studentbiljett)
