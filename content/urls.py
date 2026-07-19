from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('view/<int:content_id>/', views.content_view, name='view'),
]
