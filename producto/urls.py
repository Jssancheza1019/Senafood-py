
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_productos_view, name='lista_productos'),
    path('detalle/<int:id>/', views.detalle_producto_view, name='detalle_producto'),
    path('crear/', views.crear_producto_view, name='crear_producto'),
    path('editar/<int:id>/', views.editar_producto_view, name='editar_producto'),
    path('desactivar/<int:id>/', views.desactivar_producto_view, name='desactivar_producto'),
    path('eliminar/<int:id>/', views.eliminar_producto_view, name='eliminar_producto'),
    path('asignar-proveedor/<int:id>/', views.asignar_proveedor_view, name='asignar_proveedor'),
    path('exportar/excel/', views.exportar_excel_productos, name='exportar_excel_productos'),
    path('exportar/pdf/', views.exportar_pdf_productos, name='exportar_pdf_productos'),
]