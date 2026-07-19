from django.contrib import admin
from .models import Benegnador


@admin.register(Benegnador)
class BenegnadorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'linkedin_url']
    search_fields = ['name', 'email']
    list_filter = ['name']
