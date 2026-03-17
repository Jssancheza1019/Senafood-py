from django.shortcuts import render, redirect
from .models import Usuario, Rol  # <--- Vital: Esto conecta la lógica con tu base de datos

def login_view(request):
    if request.method == 'POST':
        email_ingresado = request.POST.get('email')
        password_ingresado = request.POST.get('password')

        try:
            # Buscamos al usuario por su email
            # Nota: Usamos 'password' porque así aparece en tu lista de campos
            usuario = Usuario.objects.get(email=email_ingresado, password=password_ingresado)
            
            # Si lo encuentra, guardamos su nombre en la sesión y vamos al Dashboard
            request.session['usuario_nombre'] = usuario.nombre
            return redirect('dashboard')
            
        except Usuario.DoesNotExist:
            # Si no existe, volvemos al login con un mensaje de error
            return render(request, 'gestion/login.html', {'error': 'Correo o contraseña incorrectos'})

    return render(request, 'gestion/login.html')

def registro_view(request):
    if request.method == 'POST':
        # 1. Captura de datos del formulario
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        password_ingresada = request.POST.get('password')
        telefono = request.POST.get('telefono')
        tipo_id = request.POST.get('tipo_identificacion')
        # Usaremos el teléfono como número de identificación temporalmente 
        # o puedes agregar un campo más al HTML
        num_id = request.POST.get('telefono') 

        # 2. Buscamos el rol 'Cliente' (id 3)
        # Usamos nombre_rol porque lo vimos en tu tabla de MySQL anteriormente
        try:
            rol_cliente = Rol.objects.get(nombre_rol='Cliente')
        except Rol.DoesNotExist:
            # Si por alguna razón no lo encuentra, lo crea
            rol_cliente = Rol.objects.create(nombre_rol='Cliente')
        
        # 3. Creamos el usuario con los nombres EXACTOS de tu lista
        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            email=email,
            password=password_ingresada,  # Nombre exacto: password
            telefono=telefono,
            tipo_identificacion=tipo_id,
            numero_identificacion=num_id, # Campo obligatorio en tu modelo
            rol=rol_cliente               # Nombre exacto: rol
        )
        nuevo_usuario.save()
        
        return redirect('login')
        
    return render(request, 'gestion/registro.html')

def dashboard_view(request):
    return render(request, 'gestion/dashboard.html')