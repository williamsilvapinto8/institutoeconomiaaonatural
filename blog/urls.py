from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('novo/', views.PostCreateView.as_view(), name='post_create'),
    path('<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<slug:slug>/editar/', views.PostUpdateView.as_view(), name='post_update'),
    path('<slug:slug>/deletar/', views.PostDeleteView.as_view(), name='post_delete'),
]
