from django.contrib import admin
from .models import TicketType, ChapterEvent, Payment, Ticket

admin.site.register(TicketType)
admin.site.register(ChapterEvent)
admin.site.register(Payment)
admin.site.register(Ticket)
