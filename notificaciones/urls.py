from django.urls import path
from . import views

urlpatterns = [
    path('api/contar/', views.contar_notificaciones, name='contar_notificaciones'),
    path('', views.lista_notificaciones, name='lista_notificaciones'),
]