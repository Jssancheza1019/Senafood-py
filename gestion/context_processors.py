def usuario_sesion(request):
    rol = request.session.get('usuario_rol', '')
    print("ROL EN SESION:", rol)
    return {
        'nombre_usuario': request.session.get('usuario_nombre', ''),
        'usuario_id': request.session.get('usuario_id', None),
        'rol_usuario': rol,
    }