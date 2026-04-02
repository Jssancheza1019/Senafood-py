from django.urls import path
from . import views

urlpatterns = [
    path('',                                       views.catalogo_view,       name='catalogo'),
    path('agregar/<int:id_producto>/',             views.agregar_carrito,     name='agregar_carrito'),
    path('carrito/',                               views.ver_carrito,         name='ver_carrito'),
    path('carrito/actualizar/<int:id_detalle>/',   views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/eliminar/<int:id_detalle>/',     views.eliminar_detalle,    name='eliminar_detalle'),
    path('carrito/contador/',                      views.contador_carrito,    name='contador_carrito'),
    path('carrito/confirmar/',                     views.confirmar_pedido,    name='confirmar_pedido'),
    path('pedido-confirmado/',                     views.pedido_confirmado,   name='pedido_confirmado'),
    path('pedidos/',                               views.vista_vendedor,      name='vista_vendedor'),
    path('pedidos/pagar/<int:id_carrito>/',        views.registrar_pago,      name='registrar_pago'),
    path('pedidos/entregar/<int:id_carrito>/',     views.confirmar_entrega,   name='confirmar_entrega'),
    path('pedidos/json/', views.pedidos_json, name='pedidos_json'),
    path('pedidos/cobrar/<int:id_carrito>/', views.cobrar_pedido, name='cobrar_pedido'),
]