from django.contrib import admin
from .models import Usuario, Rol, Producto, Pedido, Carrito, DetallePedido

# Configuración para que la lista de Usuarios sea fácil de leer
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    # Columnas que verás en la tabla principal
    list_display = ('nombre', 'apellido', 'email', 'rol', 'create_at')
    # Buscador por nombre, correo o cédula
    search_fields = ('nombre', 'email', 'numero_identificacion')
    # Filtros rápidos en la parte derecha
    list_filter = ('rol', 'tipo_identificacion')

# Configuración para el catálogo de Productos
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'stock', 'costo_unitario', 'estado')
    list_filter = ('categoria', 'estado')
    search_fields = ('nombre', 'codigo_barras')

# Configuración especial para ver el Detalle dentro del Pedido
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0  # No mostrar filas vacías adicionales

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_pedido', 'usuario', 'fecha_creacion', 'total', 'metodo_pago')
    inlines = [DetallePedidoInline]  # Esto permite ver qué productos hay en cada pedido

# Registros básicos para las demás tablas
admin.site.register(Rol)
admin.site.register(Carrito)