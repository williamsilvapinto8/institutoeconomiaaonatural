from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('events/public/', views.public_event_list, name='public_event_list'),
    path('events/public/<slug:public_slug>/', views.public_event_detail, name='public_event_detail'),
    path('events/enroll/<int:event_id>/', views.enroll_view, name='enroll_event'),
    path('events/unenroll/<int:event_id>/', views.unenroll_view, name='unenroll_event'),
    path('events/create/', views.create_evento_view, name='create_evento'),
    path('events/<int:event_id>/responses/', views.event_responses_dashboard, name='admin_event_responses'),
]
