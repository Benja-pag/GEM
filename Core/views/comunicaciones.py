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
from Core.models.usuarios import ProfesorJefe
from Core.models.cursos import AsignaturaImpartida, Clase
import json

def obtener_cursos_permitidos_docente(docente):
    """
    Obtiene los cursos donde un docente puede enviar comunicaciones.
    Incluye cursos donde imparte asignaturas y donde es profesor jefe.
    """
    cursos_disponibles = set()
    
    # 1. Cursos donde imparte asignaturas (solo asignaturas regulares, no electivos)
    asignaturas_impartidas = AsignaturaImpartida.objects.filter(docente=docente)
    for asignatura in asignaturas_impartidas:
        clases = Clase.objects.filter(asignatura_impartida=asignatura)
        for clase in clases:
            if clase.curso:  # Solo asignaturas regulares, no electivos
                cursos_disponibles.add(clase.curso)
    
    # 2. Curso donde es profesor jefe
    try:
        profesores_jefe = ProfesorJefe.objects.filter(docente=docente)
        for pj in profesores_jefe:
            if pj.curso:
                cursos_disponibles.add(pj.curso)
    except:
        pass
    
    return sorted(list(cursos_disponibles), key=lambda x: (x.nivel, x.letra))

def verificar_permisos_cursos_docente(docente, cursos_ids):
    """
    Verifica que un docente tenga permisos para enviar comunicaciones a los cursos especificados.
    """
    cursos_permitidos = set()
    
    # Obtener cursos permitidos
    cursos_disponibles = obtener_cursos_permitidos_docente(docente)
    for curso in cursos_disponibles:
        cursos_permitidos.add(str(curso.id))
    
    # Verificar que todos los cursos seleccionados estén permitidos
    for curso_id in cursos_ids:
        if curso_id not in cursos_permitidos:
            return False
    
    return True

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
    Vista para crear nuevas comunicaciones
    - Administradores: pueden enviar a todos los cursos
    - Docentes: solo a sus asignaturas y curso jefe
    """
    template_name = 'comunicaciones/crear_comunicacion.html'
    
    def get(self, request):
        # Verificar permisos básicos
        es_admin = request.user.is_superuser or (hasattr(request.user, 'usuario') and 
                                                hasattr(request.user.usuario, 'administrativo'))
        es_docente = hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'docente')
        
        if not (es_admin or es_docente):
            messages.error(request, 'No tienes permisos para crear comunicaciones')
            return redirect('bandeja_entrada')
        
        # Obtener cursos disponibles según el tipo de usuario
        if es_admin:
            # Administradores pueden enviar a todos los cursos
            cursos = Curso.objects.all().order_by('nivel', 'letra')
            es_administrador = True
        else:
            # Docentes solo pueden enviar a sus cursos
            docente = request.user.usuario.docente
            cursos = obtener_cursos_permitidos_docente(docente)
            es_administrador = False
            
            if not cursos:
                messages.warning(request, 'No tienes cursos asignados para enviar comunicaciones')
                return redirect('bandeja_entrada')
        
        context = {
            'cursos': cursos,
            'es_administrador': es_administrador
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Verificar permisos básicos
        es_admin = request.user.is_superuser or (hasattr(request.user, 'usuario') and 
                                                hasattr(request.user.usuario, 'administrativo'))
        es_docente = hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'docente')
        
        if not (es_admin or es_docente):
            return JsonResponse({'success': False, 'message': 'Sin permisos'})
        
        try:
            # Obtener cursos seleccionados
            cursos_ids = request.POST.getlist('cursos_destinatarios')
            if not cursos_ids:
                return JsonResponse({'success': False, 'message': 'Debe seleccionar al menos un curso destinatario'})
            
            # Si es docente, verificar que solo envíe a sus cursos permitidos
            if es_docente and not es_admin:
                docente = request.user.usuario.docente
                if not verificar_permisos_cursos_docente(docente, cursos_ids):
                    return JsonResponse({'success': False, 'message': 'No tienes permisos para enviar comunicaciones a uno o más cursos seleccionados'})
            
            # Crear la comunicación
            comunicacion = Comunicacion.objects.create(
                asunto=request.POST.get('asunto'),
                contenido=request.POST.get('contenido'),
                autor=request.user
            )
            
            # Agregar cursos destinatarios
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
    Vista para editar comunicaciones existentes
    - Administradores: pueden editar cualquier comunicación
    - Docentes: solo pueden editar sus propias comunicaciones y solo enviar a sus cursos permitidos
    """
    template_name = 'comunicaciones/editar_comunicacion.html'
    
    def get(self, request, comunicacion_id):
        comunicacion = get_object_or_404(Comunicacion, id=comunicacion_id)
        
        # Verificar permisos básicos
        es_admin = request.user.is_superuser or (hasattr(request.user, 'usuario') and 
                                                hasattr(request.user.usuario, 'administrativo'))
        es_docente = hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'docente')
        
        # Verificar permisos de edición
        if not (es_admin or (es_docente and comunicacion.autor == request.user)):
            messages.error(request, 'No tienes permisos para editar esta comunicación')
            return redirect('detalle_comunicacion', comunicacion_id=comunicacion_id)
        
        # Obtener cursos disponibles según el tipo de usuario
        if es_admin:
            # Administradores pueden enviar a todos los cursos
            cursos = Curso.objects.all().order_by('nivel', 'letra')
            es_administrador = True
        else:
            # Docentes solo pueden enviar a sus cursos
            docente = request.user.usuario.docente
            cursos = obtener_cursos_permitidos_docente(docente)
            es_administrador = False
        
        context = {
            'comunicacion': comunicacion,
            'cursos': cursos,
            'es_administrador': es_administrador
        }
        return render(request, self.template_name, context)
    
    def post(self, request, comunicacion_id):
        comunicacion = get_object_or_404(Comunicacion, id=comunicacion_id)
        
        # Verificar permisos básicos
        es_admin = request.user.is_superuser or (hasattr(request.user, 'usuario') and 
                                                hasattr(request.user.usuario, 'administrativo'))
        es_docente = hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'docente')
        
        # Verificar permisos de edición
        if not (es_admin or (es_docente and comunicacion.autor == request.user)):
            return JsonResponse({'success': False, 'message': 'Sin permisos para editar esta comunicación'})
        
        try:
            # Obtener cursos seleccionados
            cursos_ids = request.POST.getlist('cursos_destinatarios')
            if not cursos_ids:
                return JsonResponse({'success': False, 'message': 'Debe seleccionar al menos un curso destinatario'})
            
            # Si es docente, verificar que solo envíe a sus cursos permitidos
            if es_docente and not es_admin:
                docente = request.user.usuario.docente
                if not verificar_permisos_cursos_docente(docente, cursos_ids):
                    return JsonResponse({'success': False, 'message': 'No tienes permisos para enviar comunicaciones a uno o más cursos seleccionados'})
            
            # Actualizar comunicación
            comunicacion.asunto = request.POST.get('asunto')
            comunicacion.contenido = request.POST.get('contenido')
            comunicacion.save()
            
            # Actualizar cursos destinatarios
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
    Vista para eliminar comunicaciones
    - Administradores: pueden eliminar cualquier comunicación
    - Docentes: solo pueden eliminar sus propias comunicaciones
    """
    def post(self, request, comunicacion_id):
        comunicacion = get_object_or_404(Comunicacion, id=comunicacion_id)
        
        # Verificar permisos básicos
        es_admin = request.user.is_superuser or (hasattr(request.user, 'usuario') and 
                                                hasattr(request.user.usuario, 'administrativo'))
        es_docente = hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'docente')
        
        # Verificar permisos de eliminación
        if not (es_admin or (es_docente and comunicacion.autor == request.user)):
            return JsonResponse({'success': False, 'message': 'Sin permisos para eliminar esta comunicación'})
        
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