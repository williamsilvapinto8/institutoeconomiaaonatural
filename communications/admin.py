from django.contrib import admin
from .models import EmailLog, EmailTracking


class EmailTrackingInline(admin.TabularInline):
    model = EmailTracking
    extra = 0
    readonly_fields = ['token', 'opened_at', 'clicked_at']
    can_delete = False


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['subject', 'recipient_email', 'type', 'event', 'sent_at']
    list_filter = ['type', 'event', 'sent_at']
    search_fields = ['recipient_email', 'subject']
    readonly_fields = ['sent_at']
    inlines = [EmailTrackingInline]


@admin.register(EmailTracking)
class EmailTrackingAdmin(admin.ModelAdmin):
    list_display = ['token', 'email_log', 'opened_at', 'clicked_at']
    readonly_fields = ['token', 'opened_at', 'clicked_at']
