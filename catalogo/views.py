from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from gestion.models import Producto, Carrito, Detallecarrito, Usuario


def sesion_requerida(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_usuario(request):
    try:
        return Usuario.objects.get(id_usuario=request.session['usuario_id'])
    except Usuario.DoesNotExist:
        return None


def get_carrito_activo(usuario):
    carrito, _ = Carrito.objects.get_or_create(
        usuario=usuario,
        estado='abierto',
        defaults={'total': 0}
    )
    return carrito


# ─────────────────────────────────────────
# CATÁLOGO
# ─────────────────────────────────────────
@sesion_requerida
def catalogo_view(request):
    filtro_categoria = request.GET.get('categoria', '')
    filtro_buscar    = request.GET.get('buscar', '')

    productos = Producto.objects.filter(
        estado='activo',
        es_activo=True
    ).order_by('nombre')

    if filtro_categoria:
        productos = productos.filter(categoria=filtro_categoria)
    if filtro_buscar:
        productos = productos.filter(nombre__icontains=filtro_buscar)

    categorias = Producto.objects.filter(
        estado='activo', es_activo=True
    ).values_list('categoria', flat=True).distinct().exclude(
        categoria__isnull=True
    ).exclude(categoria='').order_by('categoria')

    usuario  = get_usuario(request)
    carrito  = get_carrito_activo(usuario)
    n_items  = Detallecarrito.objects.filter(id_carrito=carrito).count()

    return render(request, 'catalogo/catalogo.html', {
        'productos':         productos,
        'categorias':        categorias,
        'filtro_categoria':  filtro_categoria,
        'filtro_buscar':     filtro_buscar,
        'n_items':           n_items,
        'nombre_usuario':    request.session.get('usuario_nombre', ''),
        'rol_usuario':       request.session.get('usuario_rol', ''),
    })


# ─────────────────────────────────────────
# AGREGAR AL CARRITO
# ─────────────────────────────────────────
@sesion_requerida
def agregar_carrito(request, id_producto):
    producto = get_object_or_404(Producto, pk=id_producto, estado='activo', es_activo=True)
    usuario  = get_usuario(request)
    carrito  = get_carrito_activo(usuario)

    precio = producto.precio_promocion if producto.en_promocion else producto.precio_venta or producto.costo_unitario

    detalle, creado = Detallecarrito.objects.get_or_create(
        id_carrito  = carrito,
        id_producto = producto,
        defaults    = {'cantidad': 1, 'precio_unitario': precio}
    )

    if not creado:
        detalle.cantidad += 1
        detalle.save()

    # Recalcular total
    detalles = Detallecarrito.objects.filter(id_carrito=carrito)
    total    = sum(d.cantidad * d.precio_unitario for d in detalles)
    carrito.total    = total
    carrito.update_at = timezone.now()
    carrito.save()

    return redirect('catalogo')


# ─────────────────────────────────────────
# CONTADOR CARRITO (AJAX)
# ─────────────────────────────────────────
@sesion_requerida
def contador_carrito(request):
    usuario = get_usuario(request)
    carrito = get_carrito_activo(usuario)
    n_items = Detallecarrito.objects.filter(id_carrito=carrito).count()
    return JsonResponse({'total': n_items})


# ─────────────────────────────────────────
# VER CARRITO
# ─────────────────────────────────────────
@sesion_requerida
def ver_carrito(request):
    usuario  = get_usuario(request)
    carrito  = get_carrito_activo(usuario)
    detalles = Detallecarrito.objects.filter(
        id_carrito=carrito
    ).select_related('id_producto')

    total = sum(d.cantidad * d.precio_unitario for d in detalles)

    return render(request, 'catalogo/carrito.html', {
        'carrito':        carrito,
        'detalles':       detalles,
        'total':          total,
        'nombre_usuario': request.session.get('usuario_nombre', ''),
        'rol_usuario':    request.session.get('usuario_rol', ''),
    })


# ─────────────────────────────────────────
# ACTUALIZAR CANTIDAD
# ─────────────────────────────────────────
@sesion_requerida
def actualizar_cantidad(request, id_detalle):
    if request.method == 'POST':
        detalle  = get_object_or_404(Detallecarrito, pk=id_detalle)
        cantidad = int(request.POST.get('cantidad', 1))

        if cantidad <= 0:
            detalle.delete()
        else:
            detalle.cantidad = cantidad
            detalle.save()

        carrito  = detalle.id_carrito
        detalles = Detallecarrito.objects.filter(id_carrito=carrito)
        total    = sum(d.cantidad * d.precio_unitario for d in detalles)
        carrito.total = total
        carrito.save()

    return redirect('ver_carrito')


# ─────────────────────────────────────────
# ELIMINAR DETALLE
# ─────────────────────────────────────────
@sesion_requerida
def eliminar_detalle(request, id_detalle):
    detalle = get_object_or_404(Detallecarrito, pk=id_detalle)
    carrito = detalle.id_carrito
    detalle.delete()

    detalles = Detallecarrito.objects.filter(id_carrito=carrito)
    total    = sum(d.cantidad * d.precio_unitario for d in detalles)
    carrito.total = total
    carrito.save()

    return redirect('ver_carrito')