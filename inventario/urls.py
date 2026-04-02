from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.lista_inventario,          name='lista_inventario'),
    path('realizar/',               views.realizar_inventario,       name='realizar_inventario'),
    path('historial/',              views.historial_inventario,      name='historial_inventario'),
    path('detalle/<int:pk>/',       views.detalle_inventario_diario, name='detalle_inventario_diario'),
    path('exportar/pdf/<int:pk>/',  views.exportar_pdf,              name='exportar_pdf_inventario'),
    path('exportar/excel/<int:pk>/',views.exportar_excel,            name='exportar_excel_inventario'),
    path('alerta/<int:id_producto>/', views.actualizar_alerta, name='actualizar_alerta'),
    
]