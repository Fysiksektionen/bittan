from django.contrib import admin
from .models import TicketType, ChapterEvent, Payment, Ticket, SwishPaymentRequestModel


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ["title", "is_visible", "price"]

admin.site.register(SwishPaymentRequestModel)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["pk", "email", "status", "swish_id", "payment_method"]
    search_fields = ["pk", "email", "swish_id"]
    list_filter = ["status"]

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["external_id", "payment", "ticket_type", "chapter_event", "payment_status", "times_used", "payment_email"]
    list_filter = ["payment__status"]

    def payment_status(self, obj):
        return obj.payment.status if obj.payment else None

    def payment_email(self, obj):
        return obj.payment.email if obj.payment else None


@admin.register(ChapterEvent)
class ChapterEventAdmin(admin.ModelAdmin):
    list_display = ["title", "total_seats", "alive_ticket_count"]
    readonly_fields = ["alive_ticket_count"]
