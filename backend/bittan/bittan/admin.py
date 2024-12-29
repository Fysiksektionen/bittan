from django.contrib import admin
from .models import TicketType, ChapterEvent, Payment, Ticket, SwishPaymentRequestModel


admin.site.register(TicketType)
admin.site.register(SwishPaymentRequestModel)
admin.site.register(Payment)
admin.site.register(Ticket)

@admin.register(ChapterEvent)
class ChapterEventAdmin(admin.ModelAdmin):
    readonly_fields = ["alive_ticket_count"]
