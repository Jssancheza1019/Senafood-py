# usuarios/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Esta será la ruta: 127.0.0.1:8000/usuarios/lista/
    path('lista/', views.usuarios_lista_view, name='usuarios_lista'),
    # Aquí iremos agregando las rutas de eliminar y editar
]