# usuarios/views.py
from django.shortcuts import render, redirect
from gestion.models import Usuario # Importamos tu modelo desde la otra app

def usuarios_lista_view(request):
    # Verificación de seguridad (sesión)
    if 'usuario_nombre' not in request.session:
        return redirect('login')
    
    # Traemos todos los usuarios registrados en MySQL
    usuarios = Usuario.objects.all()
    
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})