#!/usr/bin/env python3

import os, sys

sys.path.append("..")
os.environ['DJANGO_SETTINGS_MODULE'] = "bittan.settings"
import django
django.setup()

from django.contrib.auth.models import User
from bittan.models import ChapterEvent

User.objects.create_superuser("admin", None, "admin")

ChapterEvent(title="Fysikalen Dag 1").save()
