from django.contrib import admin
from .models import ImpactDimension, ImpactQuestion, ImpactForm, ImpactResponse, ImpactAnswer


@admin.register(ImpactDimension)
class ImpactDimensionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'weight']


class ImpactQuestionInline(admin.TabularInline):
    model = ImpactQuestion
    extra = 0
    fields = ['order', 'text', 'is_open', 'dimension']


@admin.register(ImpactQuestion)
class ImpactQuestionAdmin(admin.ModelAdmin):
    list_display = ['order', 'dimension', 'text', 'is_open']
    list_filter = ['dimension', 'is_open']
    ordering = ['order']


@admin.register(ImpactForm)
class ImpactFormAdmin(admin.ModelAdmin):
    list_display = ['name', 'event']
    list_filter = ['event']


class ImpactAnswerInline(admin.TabularInline):
    model = ImpactAnswer
    extra = 0
    readonly_fields = ['impact_question', 'value', 'text_answer']
    can_delete = False


@admin.register(ImpactResponse)
class ImpactResponseAdmin(admin.ModelAdmin):
    list_display = ['benegnado', 'impact_form', 'created_at', 'iih_score']
    list_filter = ['impact_form__event']
    readonly_fields = ['created_at', 'iih_score']
    inlines = [ImpactAnswerInline]

    def iih_score(self, obj):
        return f'{obj.calculate_iih():.2f}'
    iih_score.short_description = 'Score IIH'
