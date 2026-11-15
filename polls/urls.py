from django.urls import path
from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('anket/<int:pk>/', views.poll_detail_view, name='detail'),
    path('anket/yeni/', views.poll_create_view, name='create'),
    path('anket/<int:pk>/oy-ver/', views.vote_view, name='vote'),
]
