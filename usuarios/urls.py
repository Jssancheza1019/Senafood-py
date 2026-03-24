# usuarios/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Como en el urls.py principal ya dice path('usuarios/', ...), 
    # estas rutas quedarán como /usuarios/lista/, /usuarios/exportar/excel/, etc.
    path('lista/', views.usuarios_lista_view, name='usuarios_lista'),
    path('exportar/excel/', views.exportar_excel, name='exportar_excel'),
    path('exportar/pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('eliminar/<int:id_usuario>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('editar/<int:id_usuario>/', views.editar_usuario, name='editar_usuario'),
]