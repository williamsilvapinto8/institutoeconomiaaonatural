from django.contrib import admin
from .models import ContentItem


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'event']
    list_filter = ['type', 'event']
    search_fields = ['title']
