from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('track/pixel/<uuid:token>/', views.pixel_view, name='track_pixel'),
    path('track/click/<uuid:token>/', views.click_view, name='track_click'),
]
