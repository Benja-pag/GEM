from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from Core.models import Comunicacion, Usuario, AdjuntoComunicacion, Curso
import json

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
        
        # Calcular estadísticas
        comunicaciones_leidas = comunicaciones.filter(leido_por=usuario_actual).count()
        comunicaciones_no_leidas = comunicaciones.exclude(leido_por=usuario_actual).count()
        total_adjuntos = sum(c.adjuntos.count() for c in comunicaciones)

        context = {
            'comunicaciones': comunicaciones,
            'comunicaciones_leidas': comunicaciones_leidas,
            'comunicaciones_no_leidas': comunicaciones_no_leidas,
            'total_adjuntos': total_adjuntos
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


@method_decorator(login_required, name='dispatch')
class CrearComunicacionView(View):
    """
    Vista para crear nuevas comunicaciones (solo administradores)
    """
    template_name = 'comunicaciones/crear_comunicacion.html'
    
    def get(self, request):
        # Verificar que sea administrador
        if not (request.user.is_superuser or hasattr(request.user, 'usuario') and 
                hasattr(request.user.usuario, 'administrativo')):
            messages.error(request, 'No tienes permisos para crear comunicaciones')
            return redirect('bandeja_entrada')
        
        # Obtener cursos para el selector
        cursos = Curso.objects.all().order_by('nivel', 'letra')
        
        context = {
            'cursos': cursos
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Verificar permisos
        if not (request.user.is_superuser or hasattr(request.user, 'usuario') and 
                hasattr(request.user.usuario, 'administrativo')):
            return JsonResponse({'success': False, 'message': 'Sin permisos'})
        
        try:
            # Crear la comunicación
            comunicacion = Comunicacion.objects.create(
                asunto=request.POST.get('asunto'),
                contenido=request.POST.get('contenido'),
                autor=request.user
            )
            
            # Agregar cursos destinatarios
            cursos_ids = request.POST.getlist('cursos_destinatarios')
            if cursos_ids:
                comunicacion.destinatarios_cursos.set(cursos_ids)
            
            # Manejar archivos adjuntos
            archivos = request.FILES.getlist('adjuntos')
            for archivo in archivos:
                AdjuntoComunicacion.objects.create(
                    comunicacion=comunicacion,
                    archivo=archivo,
                    nombre_archivo=archivo.name
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': 'Comunicación creada exitosamente',
                    'comunicacion_id': comunicacion.id
                })
            
            messages.success(request, 'Comunicación creada exitosamente')
            return redirect('detalle_comunicacion', comunicacion_id=comunicacion.id)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': str(e)})
            
            messages.error(request, f'Error al crear comunicación: {str(e)}')
            return redirect('crear_comunicacion')


@method_decorator(login_required, name='dispatch')
class EditarComunicacionView(View):
    """
    Vista para editar comunicaciones existentes (solo administradores o autores)
    """
    template_name = 'comunicaciones/editar_comunicacion.html'
    
    def get(self, request, comunicacion_id):
        comunicacion = get_object_or_404(Comunicacion, id=comunicacion_id)
        
        # Verificar permisos (admin o autor)
        if not (request.user.is_superuser or comunicacion.autor == request.user or
                hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'administrativo')):
            messages.error(request, 'No tienes permisos para editar esta comunicación')
            return redirect('detalle_comunicacion', comunicacion_id=comunicacion_id)
        
        cursos = Curso.objects.all().order_by('nivel', 'letra')
        
        context = {
            'comunicacion': comunicacion,
            'cursos': cursos
        }
        return render(request, self.template_name, context)
    
    def post(self, request, comunicacion_id):
        comunicacion = get_object_or_404(Comunicacion, id=comunicacion_id)
        
        # Verificar permisos
        if not (request.user.is_superuser or comunicacion.autor == request.user or
                hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'administrativo')):
            return JsonResponse({'success': False, 'message': 'Sin permisos'})
        
        try:
            # Actualizar comunicación
            comunicacion.asunto = request.POST.get('asunto')
            comunicacion.contenido = request.POST.get('contenido')
            comunicacion.save()
            
            # Actualizar cursos destinatarios
            cursos_ids = request.POST.getlist('cursos_destinatarios')
            comunicacion.destinatarios_cursos.set(cursos_ids)
            
            # Manejar nuevos adjuntos
            archivos = request.FILES.getlist('adjuntos')
            for archivo in archivos:
                AdjuntoComunicacion.objects.create(
                    comunicacion=comunicacion,
                    archivo=archivo,
                    nombre_archivo=archivo.name
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': 'Comunicación actualizada exitosamente'
                })
            
            messages.success(request, 'Comunicación actualizada exitosamente')
            return redirect('detalle_comunicacion', comunicacion_id=comunicacion.id)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': str(e)})
            
            messages.error(request, f'Error al actualizar comunicación: {str(e)}')
            return redirect('editar_comunicacion', comunicacion_id=comunicacion_id)


@method_decorator(login_required, name='dispatch')
class EliminarComunicacionView(View):
    """
    Vista para eliminar comunicaciones (solo administradores o autores)
    """
    def post(self, request, comunicacion_id):
        comunicacion = get_object_or_404(Comunicacion, id=comunicacion_id)
        
        # Verificar permisos
        if not (request.user.is_superuser or comunicacion.autor == request.user or
                hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'administrativo')):
            return JsonResponse({'success': False, 'message': 'Sin permisos'})
        
        try:
            titulo = comunicacion.asunto  # Guardar el título antes de eliminar
            comunicacion.delete()  # Esto elimina de la base de datos
            
            # Siempre devolver JSON para AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'success': True, 
                    'message': f'Comunicación "{titulo}" eliminada exitosamente de la base de datos'
                })
            
            messages.success(request, 'Comunicación eliminada exitosamente')
            return redirect('bandeja_entrada')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({'success': False, 'message': f'Error al eliminar de la base de datos: {str(e)}'})
            
            messages.error(request, f'Error al eliminar comunicación: {str(e)}')
            return redirect('detalle_comunicacion', comunicacion_id=comunicacion_id)


@method_decorator(login_required, name='dispatch')
class EliminarAdjuntoView(View):
    """
    Vista para eliminar adjuntos de comunicaciones
    """
    def post(self, request, adjunto_id):
        adjunto = get_object_or_404(AdjuntoComunicacion, id=adjunto_id)
        comunicacion = adjunto.comunicacion
        
        # Verificar permisos
        if not (request.user.is_superuser or comunicacion.autor == request.user or
                hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'administrativo')):
            return JsonResponse({'success': False, 'message': 'Sin permisos'})
        
        try:
            adjunto.delete()
            return JsonResponse({
                'success': True, 
                'message': 'Adjunto eliminado exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}) 