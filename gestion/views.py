from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from .models import Usuario, Rol  # <--- Vital: Esto conecta la lógica con tu base de datos
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password 
from .models import Usuario

def login_view(request):
    error_mensaje = None # Variable para guardar el error
    
    if request.method == 'POST':
        email_ingresado = request.POST.get('email')
        password_ingresada = request.POST.get('password')

        try:
            # Buscamos al usuario por email
            usuario = Usuario.objects.get(email=email_ingresado)
            
            # Verificamos la contraseña encriptada
            if check_password(password_ingresada, usuario.password):
                request.session['usuario_nombre'] = usuario.nombre
                return redirect('dashboard')
            else:
                error_mensaje = "Contraseña incorrecta. Inténtalo de nuevo."
                
        except Usuario.DoesNotExist:
            error_mensaje = "Este correo electrónico no está registrado."

    # Pasamos el error al template si existe
    # En views.py, dentro de login_view
    return render(request, 'gestion/login.html', {
        'error': error_mensaje, 
        'email_previo': email_ingresado  # Esto hace que el correo no se borre
    })

def registro_view(request):
    if request.method == 'POST':
        # 1. Captura de datos del formulario (nombres coinciden con el 'name' del HTML)
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        password_ingresada = request.POST.get('password')
        telefono = request.POST.get('telefono')
        tipo_id = request.POST.get('tipo_identificacion')
        num_id = request.POST.get('numero_identificacion') # <--- Captura el nuevo campo

        # 2. Validación básica (Evita que el sistema explote si el email ya existe)
        if Usuario.objects.filter(email=email).exists():
            return render(request, 'gestion/registro.html', {
                'error': 'Este correo ya está registrado.',
                'nombre': nombre, 'apellido': apellido # Para no borrar lo que ya escribió
            })

        # 3. Gestión del Rol
        try:
            rol_cliente = Rol.objects.get(nombre_rol='Cliente')
        except Rol.DoesNotExist:
            rol_cliente = Rol.objects.create(nombre_rol='Cliente')
        
        # 4. Encriptación
        password_segura = make_password(password_ingresada)

        # 5. Creación del objeto Usuario
        try:
            nuevo_usuario = Usuario(
                nombre=nombre,
                apellido=apellido,
                email=email,
                password=password_segura,
                telefono=telefono,
                tipo_identificacion=tipo_id,
                numero_identificacion=num_id, # <--- Ahora se guarda en su columna propia
                rol=rol_cliente 
            )
            nuevo_usuario.save()
            return redirect('login')
            
        except Exception as e:
            # En caso de cualquier otro error de base de datos
            return render(request, 'gestion/registro.html', {'error': f'Error al guardar: {e}'})
            
    return render(request, 'gestion/registro.html')



def dashboard_view(request):
    # Verificamos si la variable 'usuario_nombre' existe en la sesión
    if 'usuario_nombre' not in request.session:
        # Si no existe, significa que no se ha logueado
        return redirect('login')
    
    # Si existe, mostramos el dashboard normalmente
    return render(request, 'gestion/dashboard.html')

def login_view(request):
    error_mensaje = None
    email_ingresado = "" # <-- Agregamos esto para que la variable siempre exista

    if request.method == 'POST':
        email_ingresado = request.POST.get('email')
        password_ingresada = request.POST.get('password')

        try:
            usuario = Usuario.objects.get(email=email_ingresado)
            if check_password(password_ingresada, usuario.password):
                request.session['usuario_nombre'] = usuario.nombre
                return redirect('dashboard')
            else:
                error_mensaje = "Contraseña incorrecta."
        except Usuario.DoesNotExist:
            error_mensaje = "El correo no está registrado."

    # Ahora 'email_ingresado' siempre tiene un valor, evitando el error amarillo
    return render(request, 'gestion/login.html', {
        'error': error_mensaje, 
        'email_previo': email_ingresado
    })

def logout_view(request):
    # Borramos los datos de la sesión
    request.session.flush()
    # Redirigimos al login
    return redirect('login')