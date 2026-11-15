from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('kayit-ol/', views.register_view, name='register'),
    path('giris-yap/', views.login_view, name='login'),
    path('cikis-yap/', views.logout_view, name='logout'),
]
