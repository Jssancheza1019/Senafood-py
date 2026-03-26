from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('', include('gestion.urls')), #ruta para gestion 
    path('usuarios/', include('usuarios.urls')), # ruta para usuarios
    path('pqrsf/', include('pqrs.urls')),# ruta de pqrsf
    path('notificaciones/', include('notificaciones.urls')), # ruta notificaciones
]