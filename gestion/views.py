from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .models import Usuario, Rol 
from django.contrib.auth import logout
# Nota: Si usas un modelo manual, login_required puede fallar si no está configurado en settings.
# Usaremos la validación de sesión que ya tienes para ser consistentes.

def login_view(request):
    error_mensaje = None
    email_ingresado = "" 

    if request.method == 'POST':
        email_ingresado = request.POST.get('email')
        password_ingresada = request.POST.get('password')

        try:
            usuario = Usuario.objects.get(email=email_ingresado)
            if check_password(password_ingresada, usuario.password):
                # Guardamos ID y Nombre para usarlos en todo el sistema
                request.session['usuario_id'] = usuario.id_usuario
                request.session['usuario_nombre'] = usuario.nombre
                request.session['usuario_rol'] = usuario.rol.nombre_rol
                return redirect('dashboard')
            else:
                error_mensaje = "Contraseña incorrecta."
        except Usuario.DoesNotExist:
            error_mensaje = "El correo no está registrado."

    return render(request, 'gestion/login.html', {
        'error': error_mensaje, 
        'email_previo': email_ingresado
    })


def registro_view(request):
    usuario_id = request.session.get('usuario_id')
    es_admin = False
    
    if usuario_id:
        try:
            usuario_logueado = Usuario.objects.get(id_usuario=usuario_id)
            if usuario_logueado.rol and usuario_logueado.rol.nombre_rol == 'Administrador':
                es_admin = True
        except Usuario.DoesNotExist:
            es_admin = False

    if request.method == 'POST':
        # 1. Recoger datos
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        num_id = request.POST.get('numero_identificacion')
        id_rol_seleccionado = request.POST.get('rol')

        # --- ESCUDO DE VALIDACIÓN (Evita error 1062) ---
        
        # Validar si el email ya existe
        if Usuario.objects.filter(email=email).exists():
            return render(request, 'gestion/registro.html', {
                'error': f'El correo "{email}" ya está registrado en SenaFood.',
                'nombre': nombre, 'apellido': apellido, 'es_admin': es_admin,
                'roles': Rol.objects.all() if es_admin else None
            })

        # Validar si el número de identificación ya existe
        if Usuario.objects.filter(numero_identificacion=num_id).exists():
            return render(request, 'gestion/registro.html', {
                'error': f'El número de documento "{num_id}" ya está registrado.',
                'nombre': nombre, 'apellido': apellido, 'es_admin': es_admin,
                'roles': Rol.objects.all() if es_admin else None
            })
        
        # -----------------------------------------------

        try:
            # Lógica de asignación de Rol
            if es_admin and id_rol_seleccionado:
                rol_asignado = Rol.objects.get(id_rol=id_rol_seleccionado)
            else:
                rol_asignado, _ = Rol.objects.get_or_create(nombre_rol='Cliente')

            # Guardado de Usuario
            password_segura = make_password(request.POST.get('password'))
            nuevo_usuario = Usuario(
                nombre=nombre,
                apellido=apellido,
                email=email,
                password=password_segura,
                telefono=request.POST.get('telefono'),
                tipo_identificacion=request.POST.get('tipo_identificacion'),
                numero_identificacion=num_id,
                rol=rol_asignado 
            )
            nuevo_usuario.save()
            
            messages.success(request, f"¡Usuario {nuevo_usuario.nombre} registrado correctamente!")
            return redirect('usuarios_lista' if es_admin else 'login')
            
        except Exception as e:
            return render(request, 'gestion/registro.html', {
                'error': f'Error inesperado: {e}',
                'roles': Rol.objects.all() if es_admin else None,
                'es_admin': es_admin
            })
            
    # GET
    contexto = {
        'roles': Rol.objects.all() if es_admin else None,
        'es_admin': es_admin 
    }
    return render(request, 'gestion/registro.html', contexto)

def dashboard_view(request):
    if 'usuario_nombre' not in request.session:
        return redirect('login')
    
    # Extraemos el nombre de la sesión para pasarlo al HTML
    contexto = {
        'nombre_usuario': request.session['usuario_nombre']
    }
    return render(request, 'gestion/dashboard.html', contexto)

def perfil_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    
    usuario = Usuario.objects.get(id_usuario=request.session['usuario_id'])
    
    if request.method == 'POST':
        # 1. Recogemos los datos (Asegúrate de capturar numero_identificacion)
        nuevo_telefono = request.POST.get('telefono')
        nuevo_correo = request.POST.get('email')
        nueva_id = request.POST.get('numero_identificacion') # <--- CLAVE: Capturar este dato
        
        # 2. VALIDACIÓN: Verificar que sean numéricos y no estén vacíos
        if not nuevo_telefono.isdigit() or not nueva_id.isdigit():
            messages.error(request, "El teléfono y la identificación deben contener solo números.")
            return render(request, 'gestion/perfil.html', {'usuario': usuario})

        # 3. Actualizamos el objeto
        usuario.telefono = nuevo_telefono
        usuario.email = nuevo_correo
        usuario.numero_identificacion = nueva_id # <--- Guardar en el campo de tu modelo
        
        usuario.save()
        
        messages.success(request, "Datos actualizados con éxito.")
        return redirect('perfil')

    return render(request, 'gestion/perfil.html', {'usuario': usuario})

def cambiar_password_view(request):
    # 1. Verificación de sesión
    if 'usuario_id' not in request.session:
        return redirect('login')

    # 2. Obtener el usuario siempre (para GET y POST) usando el campo correcto
    try:
        usuario = Usuario.objects.get(id_usuario=request.session['usuario_id'])
    except Usuario.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        # 3. Recoger datos con los nombres exactos de tu HTML
        # Nota: Asegúrate que en el HTML los 'name' coincidan con estos
        old_pass = request.POST.get('password_actual') # Antes tenías 'old_password'
        new_pass = request.POST.get('nueva_password')  # Antes tenías 'new_password'
        confirm_pass = request.POST.get('confirmar_password')

        # 4. Validaciones de seguridad
        if not check_password(old_pass, usuario.password):
            messages.error(request, "La contraseña actual es incorrecta.")
            return render(request, 'gestion/cambiar_password.html')
        
        if new_pass != confirm_pass:
            messages.error(request, "Las nuevas contraseñas no coinciden.")
            return render(request, 'gestion/cambiar-password.html')

        if len(new_pass) < 8:
            messages.error(request, "La nueva contraseña debe tener al menos 8 caracteres.")
            return render(request, 'gestion/cambiar-password.html')

        # 5. Guardado seguro
        usuario.password = make_password(new_pass)
        usuario.save()
        
        messages.success(request, "Contraseña actualizada correctamente.")
        return redirect('cambiar_password') # Te sugiero volver al perfil para ver el mensaje de éxito

    return render(request, 'gestion/cambiar_password.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')

# En gestion/views.py

# En gestion/views.py
def lista_usuarios_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    
    usuario = Usuario.objects.get(id_usuario=request.session['usuario_id'])
    usuarios = Usuario.objects.all()
    
    return render(request, 'usuarios/lista.html', {
        'usuarios': usuarios,
        'nombre_usuario': usuario.nombre,
    })