from django.contrib import admin
from .models import EventType, Evento, Inscricao


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


class InscricaoInline(admin.TabularInline):
    model = Inscricao
    extra = 1


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'date', 'location', 'total_participants', 'vacancies_left', 'response_rate', 'dashboard_link', 'responses_link']
    list_filter = ['event_type', 'date', 'is_online', 'is_public_enrollment_open']
    search_fields = ['title', 'location', 'public_slug']
    filter_horizontal = ['benegnadores']
    date_hierarchy = 'date'
    readonly_fields = ['total_participants', 'response_rate', 'vacancies_left', 'dashboard_link', 'responses_link']
    inlines = [InscricaoInline]

    def dashboard_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        if not obj.pk:
            return "Salve o evento primeiro"
        url = reverse('admin:dashboard_kpi', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">Ver KPIs</a>', url)
    dashboard_link.short_description = 'Dashboard'

    def responses_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        if not obj.pk:
            return "Salve o evento primeiro"
        url = reverse('admin_event_responses', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank" style="background-color: #236B86; color: white;">Lembretes & Respostas</a>', url)
    responses_link.short_description = 'Lembretes'

    def total_participants(self, obj):
        return obj.total_participants
    total_participants.short_description = 'Participantes Confirmados'

    def vacancies_left(self, obj):
        return obj.vacancies_left
    vacancies_left.short_description = 'Vagas Restantes'

    def response_rate(self, obj):
        return f'{obj.response_rate}%'
    response_rate.short_description = 'Taxa de Resposta'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('dashboard-kpi/<int:event_id>/', self.admin_site.admin_view(self.dashboard_kpi_view), name='dashboard_kpi'),
        ]
        return custom_urls + urls

    def dashboard_kpi_view(self, request, event_id):
        from django.shortcuts import render, get_object_or_404
        from .models import Evento
        evento = get_object_or_404(Evento, pk=event_id)
        
        from impact_forms.models import ImpactResponse, ImpactDimension
        from django.db.models import Avg

        responses = ImpactResponse.objects.filter(impact_form__event=evento)
        
        # IIH calculation
        iih_list = [r.calculate_iih() for r in responses]
        iih_geral = sum(iih_list) / len(iih_list) if iih_list else 0.0

        # Dimension means
        dimensoes = []
        dimensions = ImpactDimension.objects.all()
        for dim in dimensions:
            avg = responses.filter(answers__impact_question__dimension=dim).aggregate(
                mean=Avg('answers__value')
            )['mean']
            dimensoes.append({
                'name': dim.name,
                'media': round(avg, 2) if avg else None
            })
        
        # Cancelled registrations
        cancelled_count = evento.inscricoes.filter(status='CANCELLED').count()

        context = dict(
            self.admin_site.each_context(request),
            title=f'KPI Dashboard - {evento.title}',
            evento=evento,
            iih_geral=round(iih_geral, 2),
            dimensoes=dimensoes,
            cancelled_count=cancelled_count,
        )
        return render(request, 'admin/events/evento/dashboard_kpi.html', context)
