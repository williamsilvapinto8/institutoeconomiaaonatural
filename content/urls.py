from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('sobre/', views.sobre_view, name='sobre'),
    path('content/view/<int:content_id>/', views.content_view, name='view'),
]
