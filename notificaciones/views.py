from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Notificacion

def contar_notificaciones(request):
    usuario_id = request.session.get('usuario_id')
    
    if not usuario_id:
        return JsonResponse({'total': 0})
    
    total = Notificacion.objects.filter(
        usuario_id=usuario_id,
        leida=False
    ).count()
    
    return JsonResponse({'total': total})

def lista_notificaciones(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    # Primero obtén las notificaciones (aún con leida=False)
    notificaciones = Notificacion.objects.filter(
        usuario_id=usuario_id
    ).order_by('-fechaenvio')

    # Renderiza primero
    response = render(request, 'notificaciones/lista.html', {
        'notificaciones': notificaciones,
        'nombre_usuario': request.session.get('usuario_nombre', ''),
        'rol_usuario': request.session.get('usuario_rol', ''),
    })

    # Luego marca como leídas
    Notificacion.objects.filter(
        usuario_id=usuario_id,
        leida=False
    ).update(leida=True)

    return response
