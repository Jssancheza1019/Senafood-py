import datetime

class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar expiración por inactividad (30 minutos)
        if 'usuario_id' in request.session:
            ultima_actividad = request.session.get('ultima_actividad')
            if ultima_actividad:
                ultima = datetime.datetime.fromisoformat(ultima_actividad)
                ahora = datetime.datetime.now()
                if (ahora - ultima).total_seconds() > 1800:
                    request.session.flush()
                    from django.shortcuts import redirect
                    return redirect('login')
            request.session['ultima_actividad'] = datetime.datetime.now().isoformat()

        response = self.get_response(request)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response