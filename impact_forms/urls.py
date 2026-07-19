from django.urls import path
from . import views

app_name = 'impact_forms'

urlpatterns = [
    path('respond/<int:form_id>/', views.respond_view, name='impact_respond'),
    path('success/', views.success_view, name='impact_success'),
]

