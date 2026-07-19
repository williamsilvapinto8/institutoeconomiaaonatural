from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Benegnado


class BenegnadoInline(admin.StackedInline):
    model = Benegnado
    can_delete = False
    verbose_name_plural = 'Perfil Benegnado'


class CustomUserAdmin(UserAdmin):
    inlines = [BenegnadoInline]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Benegnado)
class BenegnadoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'phone', 'company', 'city']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'company']
    list_filter = ['city']
