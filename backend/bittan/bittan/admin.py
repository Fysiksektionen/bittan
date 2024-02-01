from django.contrib import admin
from .models import TicketType, ChapterEvent, Payment, Ticket
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.detail import DetailView
from django.urls import path, reverse
from django.utils.html import format_html


admin.site.register(TicketType)
#admin.site.register(ChapterEvent)
admin.site.register(Payment)
admin.site.register(Ticket)

#class ChapterEventInline(admin.TabularInline):
#    model = ChapterEvent

@admin.register(ChapterEvent)
class ChapterEventAdmin(admin.ModelAdmin):
    list_display = ["title", "description", "max_tickets", "detail"]
    #inlines = [ChapterEventInline]

    def get_urls(self):
        return [
            path(
                "<pk>/detail",
                self.admin_site.admin_view(ChapterEventDetailView.as_view()),
                name=f"bittan_chapterevent_details"
            ),
            *super().get_urls(),
        ]

    def detail(self, obj: ChapterEvent) -> str:
        url = reverse("admin:bittan_chapterevent_details", args=[obj.pk])
        return format_html(f'<a href="{url}">📝</a>')

class ChapterEventDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "bittan.view_chapter_events"
    template_name = "admin/bittan/chapterevent/details.html"
    model = ChapterEvent
    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,

        }

