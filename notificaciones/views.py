from django.shortcuts import render
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
        from django.shortcuts import redirect
        return redirect('login')

    notificaciones = Notificacion.objects.filter(
        usuario_id=usuario_id
    ).order_by('-fechaenvio')

    # Marcar todas como leídas al abrir la página
    Notificacion.objects.filter(
        usuario_id=usuario_id,
        leida=False
    ).update(leida=True)

    return render(request, 'notificaciones/lista.html', {
        'notificaciones': notificaciones,
        'nombre_usuario': request.session.get('usuario_nombre', ''),
        'rol_usuario': request.session.get('usuario_rol', ''),
    })
