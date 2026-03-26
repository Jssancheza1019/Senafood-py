from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.lista_pqrsf_view, name='lista_pqrsf'),
    path('crear/', views.crear_pqrsf_view, name='crear_pqrsf'),
    path('detalle/<int:id>/', views.detalle_pqrsf_view, name='detalle_pqrsf'),
    path('exportar/excel/', views.exportar_excel_pqrsf, name='exportar_excel_pqrsf'),
    path('exportar/pdf/', views.exportar_pdf_pqrsf, name='exportar_pdf_pqrsf'),
]