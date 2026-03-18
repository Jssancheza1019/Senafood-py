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
    if request.method == 'POST':
        # 1. Recoger datos del formulario
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        password_ingresada = request.POST.get('password')
        telefono = request.POST.get('telefono')
        tipo_id = request.POST.get('tipo_identificacion')
        num_id = request.POST.get('numero_identificacion')

        # 2. VALIDACIÓN: Verificar si el correo ya existe
        if Usuario.objects.filter(email=email).exists():
            return render(request, 'gestion/registro.html', {
                'error': 'Este correo ya está registrado.',
                'nombre': nombre, 'apellido': apellido, 'email': email,
                'telefono': telefono, 'numero_identificacion': num_id
            })

        # 3. VALIDACIÓN: Solo letras en Nombre y Apellido
        # Permitimos espacios para nombres/apellidos compuestos
        if not nombre.replace(" ", "").isalpha() or not apellido.replace(" ", "").isalpha():
            return render(request, 'gestion/registro.html', {
                'error': 'El nombre y el apellido solo pueden contener letras.',
                'nombre': nombre, 'apellido': apellido, 'email': email,
                'telefono': telefono, 'numero_identificacion': num_id
            })

        # 4. VALIDACIÓN: Solo números en teléfono e identificación
        if not telefono.isdigit() or not num_id.isdigit():
            return render(request, 'gestion/registro.html', {
                'error': 'El teléfono y la identificación deben contener solo números.',
                'nombre': nombre, 'apellido': apellido, 'email': email,
                'telefono': telefono, 'numero_identificacion': num_id
            })

        try:
            # 5. Lógica de guardado
            rol_cliente, created = Rol.objects.get_or_create(nombre_rol='Cliente')
            password_segura = make_password(password_ingresada)

            nuevo_usuario = Usuario(
                nombre=nombre,
                apellido=apellido,
                email=email,
                password=password_segura,
                telefono=telefono,
                tipo_identificacion=tipo_id,
                numero_identificacion=num_id,
                rol=rol_cliente 
            )
            nuevo_usuario.save()
            
            messages.success(request, "¡Registro exitoso! Ya puedes iniciar sesión.")
            return redirect('login')
            
        except Exception as e:
            return render(request, 'gestion/registro.html', {
                'error': f'Error al guardar: {e}',
                'nombre': nombre, 'apellido': apellido, 'email': email,
                'telefono': telefono, 'numero_identificacion': num_id
            })
            
    return render(request, 'gestion/registro.html')

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