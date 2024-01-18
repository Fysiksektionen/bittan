#!/usr/bin/env python3

import os, sys

sys.path.append("..")
os.environ['DJANGO_SETTINGS_MODULE'] = "bittan.settings"
import django
django.setup()

from django.contrib.auth.models import User
from bittan.models import TicketType, ChapterEvent

User.objects.create_superuser("admin", None, "admin")

TicketType(price=199.99, title="Standardbiljett", description="En vanlig biljett.").save()
TicketType(price=99.50, title="Studentbiljett", description="En billigare biljett.").save()

ChapterEvent(title="Fysikalen Dag 1").save()
