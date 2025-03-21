from django.contrib import admin
from .models import TicketType, ChapterEvent, Payment, Ticket, SwishPaymentRequestModel


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ["title", "is_visible", "price"]

admin.site.register(SwishPaymentRequestModel)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["pk", "email", "status", "swish_id", "payment_method"]

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["external_id", "payment", "ticket_type", "chapter_event"]


@admin.register(ChapterEvent)
class ChapterEventAdmin(admin.ModelAdmin):
    list_display = ["title", "total_seats", "alive_ticket_count"]
    readonly_fields = ["alive_ticket_count"]
