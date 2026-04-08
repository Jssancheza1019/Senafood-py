from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from gestion.models import Producto, Carrito, Detallecarrito, Usuario
from datetime import date
from django.db import models
from django.contrib import messages


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
    from django.contrib import messages
    producto = get_object_or_404(Producto, pk=id_producto, estado='activo', es_activo=True)
    usuario  = get_usuario(request)
    carrito  = get_carrito_activo(usuario)

    # Verificar stock disponible
    if (producto.stock or 0) <= 0:
        messages.error(request, f'"{producto.nombre}" no tiene stock disponible.')
        return redirect('catalogo')

    precio = producto.precio_promocion if producto.en_promocion else producto.precio_venta or producto.costo_unitario

    detalle, creado = Detallecarrito.objects.get_or_create(
        id_carrito  = carrito,
        id_producto = producto,
        defaults    = {'cantidad': 1, 'precio_unitario': precio}
    )

    if not creado:
        # Verificar que no supere el stock disponible
        if detalle.cantidad >= (producto.stock or 0):
            messages.error(request, f'No hay más stock disponible de "{producto.nombre}". Stock máximo: {producto.stock}.')
            return redirect('catalogo')
        detalle.cantidad += 1
        detalle.save()

    # Recalcular total
    detalles = Detallecarrito.objects.filter(id_carrito=carrito)
    total    = sum(d.cantidad * d.precio_unitario for d in detalles)
    carrito.total     = total
    carrito.update_at = timezone.now()
    carrito.save()

    messages.success(request, f'"{producto.nombre}" agregado al carrito.')
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

# CONFIRMAR PEDIDO (cliente)
@sesion_requerida
def confirmar_pedido(request):
    from django.contrib import messages
    usuario = get_usuario(request)
    carrito = get_carrito_activo(usuario)

    detalles = Detallecarrito.objects.filter(id_carrito=carrito).select_related('id_producto')

    if not detalles.exists():
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('ver_carrito')

    errores = []
    for d in detalles:
        stock_disponible = d.id_producto.stock or 0
        if d.cantidad > stock_disponible:
            errores.append(
                f'"{d.id_producto.nombre}" — solicitaste {d.cantidad} pero solo hay {stock_disponible} disponibles.'
            )

    if errores:
        for error in errores:
            messages.error(request, error)
        return redirect('ver_carrito')

    carrito.estado             = 'pendiente_pago'
    carrito.fecha_confirmacion = timezone.now()
    carrito.update_at          = timezone.now()
    carrito.save()

    return redirect('pedido_confirmado')
# ─────────────────────────────────────────
# PEDIDO CONFIRMADO (cliente)
# ─────────────────────────────────────────
@sesion_requerida
def pedido_confirmado(request):
    return render(request, 'catalogo/confirmado.html', {
        'nombre_usuario': request.session.get('usuario_nombre', ''),
        'rol_usuario':    request.session.get('usuario_rol', ''),
    })


# ─────────────────────────────────────────
# VISTA VENDEDOR
# ─────────────────────────────────────────
@sesion_requerida
def vista_vendedor(request):
    rol = request.session.get('usuario_rol', '')
    if rol not in ['Vendedor', 'Administrador', 'Cajero']:
        return redirect('dashboard')

    pedidos_caja = Carrito.objects.filter(
        estado='pendiente_pago'
    ).prefetch_related('detallecarrito_set__id_producto').order_by('create_at')

    pedidos_entrega = Carrito.objects.filter(
        estado='pendiente_entrega'
    ).prefetch_related('detallecarrito_set__id_producto').order_by('create_at')

    return render(request, 'catalogo/vendedor.html', {
        'pedidos_caja':    pedidos_caja,
        'pedidos_entrega': pedidos_entrega,
        'nombre_usuario':  request.session.get('usuario_nombre', ''),
        'rol_usuario':     request.session.get('usuario_rol', ''),
    })


# ─────────────────────────────────────────
# REGISTRAR PAGO (cajero)
# ─────────────────────────────────────────
@sesion_requerida
def registrar_pago(request, id_carrito):
    rol = request.session.get('usuario_rol', '')
    if rol not in ['Vendedor', 'Administrador', 'Cajero']:
        return redirect('dashboard')

    carrito = get_object_or_404(Carrito, pk=id_carrito, estado='pendiente_pago')
    carrito.estado     = 'pendiente_entrega'
    carrito.metodopago = 'efectivo'
    carrito.update_at  = timezone.now()
    carrito.save()

    # Agregamos el mensaje de confirmación
    messages.success(request, f"¡Pedido #{id_carrito} cobrado! Ya puedes entregar el producto.")

    # Redireccionamos a la lista de pedidos para cobrar el siguiente
    return redirect('vista_cajero')
# ─────────────────────────────────────────
# Notificar stock bajo
# ─────────────────────────────────────────
def notificar_stock_bajo(producto):
    from notificaciones.models import Notificacion
    from inventario.models import Inventario

    try:
        inv = Inventario.objects.get(idproducto=producto.id_producto)
        alerta_min = inv.alerta_minimos
    except Inventario.DoesNotExist:
        alerta_min = 5

    if (producto.stock or 0) <= alerta_min:
        admins = Usuario.objects.filter(
            rol__nombre_rol='Administrador',
            es_activo=True
        )
        for admin in admins:
            ya_notificado = Notificacion.objects.filter(
                usuario=admin,
                tipo='stock',        # ← corregido
                leida=False,
                mensaje__icontains=producto.nombre
            ).exists()

            if not ya_notificado:
                Notificacion.objects.create(
                    usuario = admin,
                    tipo    = 'stock',  # ← corregido
                    mensaje = f'Stock bajo: "{producto.nombre}" tiene {producto.stock} unidades (mínimo: {alerta_min})',
                )


# ─────────────────────────────────────────
# CONFIRMAR ENTREGA — actualizado
# ─────────────────────────────────────────
@sesion_requerida
def confirmar_entrega(request, id_carrito):
    rol = request.session.get('usuario_rol', '')
    if rol not in ['Vendedor', 'Administrador', 'Cajero']:
        return redirect('dashboard')

    carrito  = get_object_or_404(Carrito, pk=id_carrito, estado='pendiente_entrega')
    detalles = Detallecarrito.objects.filter(id_carrito=carrito)

    for d in detalles:
        producto       = d.id_producto
        producto.stock = max(0, (producto.stock or 0) - d.cantidad)

        if producto.stock <= 0:
            producto.estado = 'agotado'
        elif producto.fecha_vencimiento and producto.fecha_vencimiento < date.today():
            producto.estado = 'vencido'
        else:
            producto.estado = 'activo'

        producto.update_at = timezone.now()
        producto.save()

        # Verificar stock y notificar si está bajo
        notificar_stock_bajo(producto)

    carrito.estado        = 'entregado'
    carrito.fecha_entrega = timezone.now()
    carrito.update_at     = timezone.now()
    carrito.save()

    return redirect('vista_vendedor')

@sesion_requerida
def pedidos_json(request):
    
    rol = request.session.get('usuario_rol', '')
    if rol not in ['Vendedor', 'Administrador', 'Cajero']:
        return JsonResponse({'error': 'Sin permisos'}, status=403)

    pedidos_caja = []
    for pedido in Carrito.objects.filter(estado='pendiente_pago').order_by('create_at'):
        detalles = []
        for d in Detallecarrito.objects.filter(id_carrito=pedido).select_related('id_producto'):
            detalles.append({
                'nombre':   d.id_producto.nombre,
                'cantidad': d.cantidad,
                'subtotal': float(d.cantidad * d.precio_unitario),
            })
        pedidos_caja.append({
            'id':       pedido.id_carrito,
            'cliente':  f'{pedido.usuario.nombre} {pedido.usuario.apellido}',
            'total':    float(pedido.total or 0),
            'detalles': detalles,
        })

    pedidos_entrega = []
    for pedido in Carrito.objects.filter(estado='pendiente_entrega').order_by('create_at'):
        detalles = []
        for d in Detallecarrito.objects.filter(id_carrito=pedido).select_related('id_producto'):
            detalles.append({
                'nombre':   d.id_producto.nombre,
                'cantidad': d.cantidad,
                'subtotal': float(d.cantidad * d.precio_unitario),
            })
        pedidos_entrega.append({
            'id':       pedido.id_carrito,
            'cliente':  f'{pedido.usuario.nombre} {pedido.usuario.apellido}',
            'total':    float(pedido.total or 0),
            'detalles': detalles,
        })

    return JsonResponse({
        'pedidos_caja':    pedidos_caja,
        'pedidos_entrega': pedidos_entrega,
    })

@sesion_requerida
def cobrar_pedido(request, id_carrito):
    rol = request.session.get('usuario_rol', '')
    if rol not in ['Vendedor', 'Administrador', 'Cajero']:
        return redirect('dashboard')

    carrito  = get_object_or_404(Carrito, pk=id_carrito, estado='pendiente_pago')
    detalles = Detallecarrito.objects.filter(
        id_carrito=carrito
    ).select_related('id_producto')

    return render(request, 'catalogo/cobrar.html', {
        'carrito':        carrito,
        'detalles':       detalles,
        'nombre_usuario': request.session.get('usuario_nombre', ''),
        'rol_usuario':    request.session.get('usuario_rol', ''),
    })

@sesion_requerida
def vista_cajero(request):
    rol = request.session.get('usuario_rol', '')
    if rol not in ['Cajero', 'Administrador']:
        return redirect('dashboard')

    import datetime
    hoy = datetime.date.today()

    pedidos_pago = Carrito.objects.filter(
        estado='pendiente_pago'
    ).prefetch_related('detallecarrito_set__id_producto').order_by('create_at')

    historial_hoy = Carrito.objects.filter(
        estado__in=['pendiente_entrega', 'entregado'],
        fecha_confirmacion__date=hoy
    ).prefetch_related('detallecarrito_set__id_producto').order_by('-fecha_confirmacion')

    productos = Producto.objects.filter(
        estado='activo',
        es_activo=True
    ).order_by('nombre')

    total_dia = sum(c.total or 0 for c in historial_hoy)

    return render(request, 'catalogo/cajero.html', {
        'pedidos_pago':    pedidos_pago,
        'historial_hoy':   historial_hoy,
        'productos':       productos,
        'total_dia':       total_dia,
        'nombre_usuario':  request.session.get('usuario_nombre', ''),
        'rol_usuario':     rol,
    })


@sesion_requerida
def cajero_agregar_item(request):
    rol = request.session.get('usuario_rol', '')
    if rol not in ['Cajero', 'Administrador']:
        return JsonResponse({'error': 'Sin permisos'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    import json
    data       = json.loads(request.body)
    items      = data.get('items', [])
    usuario_id = data.get('usuario_id')

    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)

    carrito = Carrito.objects.create(
        usuario           = usuario,
        estado            = 'pendiente_pago',
        total             = 0,
        fecha_confirmacion = timezone.now(),
    )

    total = 0
    for item in items:
        try:
            producto = Producto.objects.get(pk=item['id'], estado='activo', es_activo=True)
            cantidad = int(item['cantidad'])
            precio   = producto.precio_promocion if producto.en_promocion else producto.precio_venta or producto.costo_unitario
            Detallecarrito.objects.create(
                id_carrito      = carrito,
                id_producto     = producto,
                cantidad        = cantidad,
                precio_unitario = precio,
            )
            total += cantidad * precio
        except Producto.DoesNotExist:
            continue

    carrito.total = total
    carrito.save()

    return JsonResponse({'ok': True, 'carrito_id': carrito.id_carrito, 'total': float(total)})


@sesion_requerida
def buscar_cliente(request):
    rol = request.session.get('usuario_rol', '')
    if rol not in ['Cajero', 'Administrador']:
        return JsonResponse({'error': 'Sin permisos'}, status=403)

    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'clientes': []})

    clientes = Usuario.objects.filter(
        es_activo=True,
        rol__nombre_rol='Cliente'
    ).filter(
        models.Q(nombre__icontains=q) |
        models.Q(apellido__icontains=q) |
        models.Q(email__icontains=q)
    )[:10]

    return JsonResponse({'clientes': [
        {'id': c.id_usuario, 'nombre': f'{c.nombre} {c.apellido}', 'email': c.email}
        for c in clientes
    ]})

@sesion_requerida
def cajero_crear_cliente_rapido(request):
    rol = request.session.get('usuario_rol', '')
    if rol not in ['Cajero', 'Administrador']:
        return JsonResponse({'error': 'Sin permisos'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    import json
    from django.contrib.auth.hashers import make_password
    from gestion.models import Rol

    data   = json.loads(request.body)
    nombre = data.get('nombre', '').strip()
    cedula = data.get('cedula', '').strip()

    if not nombre or not cedula:
        return JsonResponse({'error': 'Nombre y cédula son obligatorios'}, status=400)

    if Usuario.objects.filter(numero_identificacion=cedula).exists():
        cliente = Usuario.objects.get(numero_identificacion=cedula)
        return JsonResponse({
            'ok': True,
            'id': cliente.id_usuario,
            'nombre': f'{cliente.nombre} {cliente.apellido or ""}',
            'existia': True
        })

    try:
        rol_cliente = Rol.objects.get(nombre_rol='Cliente')
    except Rol.DoesNotExist:
        return JsonResponse({'error': 'Rol Cliente no encontrado'}, status=500)

    partes    = nombre.split(' ', 1)
    nombre_us = partes[0]
    apellido  = partes[1] if len(partes) > 1 else ''

    email = f"caja_{cedula}@senafood.local"

    cliente = Usuario.objects.create(
        nombre                = nombre_us,
        apellido              = apellido,
        email                 = email,
        password              = make_password(cedula),
        numero_identificacion = cedula,
        tipo_identificacion   = 'CC',
        rol                   = rol_cliente,
        es_activo             = True,
    )

    return JsonResponse({
        'ok': True,
        'id': cliente.id_usuario,
        'nombre': f'{cliente.nombre} {cliente.apellido}',
        'existia': False
    })