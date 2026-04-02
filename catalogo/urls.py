from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.catalogo_view,     name='catalogo'),
    path('agregar/<int:id_producto>/',    views.agregar_carrito,   name='agregar_carrito'),
    path('carrito/',                      views.ver_carrito,       name='ver_carrito'),
    path('carrito/actualizar/<int:id_detalle>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/eliminar/<int:id_detalle>/',   views.eliminar_detalle,    name='eliminar_detalle'),
    path('carrito/contador/',             views.contador_carrito,  name='contador_carrito'),
]