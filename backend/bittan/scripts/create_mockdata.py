#!/usr/bin/env python3

import os, sys

sys.path.append("..")
os.environ['DJANGO_SETTINGS_MODULE'] = "bittan.settings"
import django
django.setup()

from bittan.models import ChapterEvent

ChapterEvent(title="Fysikalen Dag 1").save()
