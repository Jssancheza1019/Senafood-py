# usuarios/views.py
import openpyxl
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.shortcuts import render, redirect
from django.http import HttpResponse
from gestion.models import Usuario, Rol # Importamos tu modelo desde la otra app

def usuarios_lista_view(request):
    # Mantienes tu verificación de seguridad (esto está perfecto)
    if 'usuario_nombre' not in request.session:
        return redirect('login')
    
    usuarios = Usuario.objects.all().order_by('-es_activo', 'nombre')
    # Conteos   
    total_activos    = Usuario.objects.filter(es_activo=True).count()
    total_inactivos  = Usuario.objects.filter(es_activo=False).count()
    total_admins     = Usuario.objects.filter(rol__nombre_rol='Administrador').count()
    total_vendedores = Usuario.objects.filter(rol__nombre_rol='Vendedor').count()
    total_clientes   = Usuario.objects.filter(rol__nombre_rol='Cliente').count()

    return render(request, 'usuarios/lista.html', {
        'usuarios':         usuarios,
        'total_activos':    total_activos,
        'total_inactivos':  total_inactivos,
        'total_admins':     total_admins,
        'total_vendedores': total_vendedores,
        'total_clientes':   total_clientes,
    })

# FUNCIÓN ELIMINAR
def eliminar_usuario(request, id_usuario):
    # 1. Buscamos al usuario
    usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
    
    # 2. BORRADO LÓGICO: Solo cambiamos el estado a False
    # Esto NO dispara el IntegrityError porque el usuario sigue existiendo en la DB
    usuario.es_activo = False
    usuario.save()
    
    messages.success(request, f"Usuario {usuario.nombre} desactivado correctamente. Se mantiene el historial de compras.")
    return redirect('usuarios_lista')

# FUNCIÓN EDITAR (Carga el formulario con datos)
def editar_usuario(request, id_usuario):
    usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
    roles = Rol.objects.all()

    if request.method == 'POST':
        usuario.nombre = request.POST.get('nombre')
        usuario.apellido = request.POST.get('apellido')
        usuario.numero_identificacion = request.POST.get('numero_identificacion')
        usuario.email = request.POST.get('email')
        usuario.telefono = request.POST.get('telefono')
        # Actualizar Rol
        id_rol = request.POST.get('rol')
        usuario.rol = Rol.objects.get(id_rol=id_rol)
        
        usuario.save()
        messages.success(request, "Usuario actualizado correctamente.")
        return redirect('usuarios_lista')

    return render(request, 'usuarios/editar.html', {'usuario': usuario, 'roles': roles})

def exportar_excel(request):
    # Crear el libro de trabajo
    wb = openpyxl.Workbook()
    hoja = wb.active
    hoja.title = "SenaFood Usuarios"

    # Estilo básico para encabezados
    hoja.append(['Nombre', 'Apellido', 'Email', 'Teléfono', 'Identificación'])

    # Agregar los datos
    usuarios = Usuario.objects.all()
    for u in usuarios:
        hoja.append([u.nombre, u.apellido, u.email, u.telefono, u.numero_identificacion])

    # Configurar la respuesta para descarga
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="informe_usuarios.xlsx"'
    wb.save(response)
    return response

# Función provisional para PDF (para que no de error)
def exportar_pdf(request):
    # Configurar la respuesta
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Informe_Usuarios_SenaFood.pdf"'

    # Crear el documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Datos para la tabla
    data = [['Nombre', 'Email', 'Teléfono', 'Identificación']]
    usuarios = Usuario.objects.all()
    
    for u in usuarios:
        data.append([
            f"{u.nombre} {u.apellido}",
            u.email,
            u.telefono,
            u.numero_identificacion
        ])

    # Crear la tabla y darle estilo (Colores SENA)
    tabla = Table(data)
    estilo = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#39A900')), # Verde SENA
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    tabla.setStyle(estilo)
    
    elements.append(tabla)
    doc.build(elements)
    
    return response