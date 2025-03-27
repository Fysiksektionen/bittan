from django.contrib import admin
from django.db.models import Sum
from django.urls import reverse
from django.utils.html import format_html

from .models import TicketType, ChapterEvent, Payment, Ticket, SwishPaymentRequestModel

@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ["title", "is_visible", "price"]

admin.site.register(SwishPaymentRequestModel)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["pk", "email", "status", "swish_id", "payment_method", "payment_value"]
    search_fields = ["pk", "email", "swish_id"]
    list_filter = ["status"]

    def payment_value(self, obj):
        return obj.ticket_set.aggregate(Sum("ticket_type__price"))["ticket_type__price__sum"]

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["external_id", "payment_link", "ticket_type", "chapter_event", "payment_status", "times_used", "payment_email"]
    list_filter = ["payment__status"]
    search_fields = ["payment__swish_id", "external_id", "payment__email"]

    def payment_status(self, obj):
        return obj.payment.status if obj.payment else None

    def payment_email(self, obj):
        return obj.payment.email if obj.payment else None

    def payment_link(self, obj):
        if obj.payment:
            url = reverse("admin:bittan_payment_change", args=[obj.payment.pk])
            return format_html('<a href="{}">{}</a>', url, obj.payment)
    payment_link.short_description = "Payment"

@admin.register(ChapterEvent)
class ChapterEventAdmin(admin.ModelAdmin):
    list_display = ["title", "total_seats", "alive_ticket_count"]
    readonly_fields = ["alive_ticket_count"]
