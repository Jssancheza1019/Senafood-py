from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('', include('gestion.urls')), #ruta para gestion 
    path('usuarios/', include('usuarios.urls')), # ruta para usuarios
]