from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from Core.models import Comunicacion, Usuario

@method_decorator(login_required, name='dispatch')
class BandejaEntradaView(View):
    """
    Muestra la bandeja de entrada de comunicaciones para el usuario logueado.
    """
    template_name = 'comunicaciones/bandeja_entrada.html'

    def get(self, request):
        usuario_actual = request.user
        
        # Obtener el curso del estudiante, si aplica
        curso_usuario = None
        if hasattr(usuario_actual, 'usuario') and hasattr(usuario_actual.usuario, 'estudiante'):
            curso_usuario = usuario_actual.usuario.estudiante.curso

        # Filtrar comunicaciones:
        # 1. Donde el usuario es destinatario directo.
        # 2. Donde el curso del usuario es destinatario (si tiene curso).
        query = Q(destinatarios_usuarios=usuario_actual)
        if curso_usuario:
            query |= Q(destinatarios_cursos=curso_usuario)
        
        comunicaciones = Comunicacion.objects.filter(query).distinct().order_by('-fecha_envio')

        context = {
            'comunicaciones': comunicaciones
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class ComunicacionDetalleView(View):
    """
    Muestra el detalle de una comunicación y la marca como leída.
    """
    template_name = 'comunicaciones/detalle_comunicacion.html'

    def get(self, request, comunicacion_id):
        comunicacion = get_object_or_404(Comunicacion, id=comunicacion_id)
        
        # Marcar como leída para el usuario actual
        comunicacion.leido_por.add(request.user)
        
        context = {
            'comunicacion': comunicacion
        }
        return render(request, self.template_name, context) 