from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_ventas, name='lista_ventas'),
    path('detalle/<int:id_carrito>/', views.detalle_venta, name='detalle_venta'),
    path('exportar/pdf/', views.exportar_pdf_ventas, name='exportar_pdf_ventas'),
    path('exportar/excel/', views.exportar_excel_ventas, name='exportar_excel_ventas'),
]