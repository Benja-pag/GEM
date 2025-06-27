from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from Core.models import Usuario, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura, AsignaturaImpartida, Curso, ProfesorJefe, AlumnoEvaluacion, Comunicacion
from django.db.models import Count, Avg, Max, Q
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from Core.servicios.repos import usuarios
from Core.servicios.helpers import validadores, serializadores
from Core.servicios.repos.cursos import get_curso, get_estudiantes_por_curso
from Core.servicios.alumnos.helpers import get_promedio_estudiante, get_asistencia_estudiante
from django.core.exceptions import PermissionDenied
import json

@method_decorator(login_required, name='dispatch')
class CursoDetalleView(View):
    def get(self, request, curso_id):
        curso = get_object_or_404(Curso, id=curso_id)
        
        # VALIDACIÓN DE PERMISOS
        # Verificar si el usuario es administrador
        es_admin = hasattr(request.user.usuario, 'administrativo')
        
        # Verificar si el usuario es docente
        if not es_admin and not hasattr(request.user.usuario, 'docente'):
            messages.error(request, 'No tienes permisos para acceder a este curso')
            return redirect('home')
        
        if not es_admin:  # Si no es admin, verificar permisos de docente
            docente = request.user.usuario.docente
            
            # Verificar si es profesor jefe del curso
            es_profesor_jefe = ProfesorJefe.objects.filter(
                docente=docente, 
                curso=curso
            ).exists()
            
            # Verificar si imparte alguna asignatura en el curso
            imparte_en_curso = AsignaturaImpartida.objects.filter(
                docente=docente,
                clases__curso=curso
            ).exists()
            
            # Si no es profesor jefe ni imparte en el curso, denegar acceso
            if not (es_profesor_jefe or imparte_en_curso):
                messages.error(request, f'No tienes permisos para acceder al curso {curso.nivel}°{curso.letra}. Solo pueden acceder profesores jefe o docentes que imparten asignaturas en este curso.')
                return redirect('profesor_panel')
        
        # Obtener estudiantes del curso
        estudiantes = Estudiante.objects.filter(curso=curso).select_related('usuario')
        
        # Obtener asignaturas impartidas en el curso
        asignaturas = AsignaturaImpartida.objects.filter(
            clases__curso=curso
        ).select_related(
            'asignatura',
            'docente__usuario'
        ).distinct()
        
        # Obtener profesor jefe
        profesor_jefe = ProfesorJefe.objects.filter(
            curso=curso
        ).select_related('docente__usuario').first()
        
        # Calcular ranking de estudiantes
        ranking_estudiantes = []
        for estudiante in estudiantes:
            # Calcular promedio general del estudiante
            promedio_general = get_promedio_estudiante(estudiante.pk)
            
            # Calcular asistencia general del estudiante
            asistencia_data = get_asistencia_estudiante(estudiante.pk)
            total_asistencias = sum(data['total'] for data in asistencia_data.values())
            total_presentes = sum(data['presentes'] for data in asistencia_data.values())
            porcentaje_asistencia = (total_presentes / total_asistencias * 100) if total_asistencias > 0 else 0
            
            # Encontrar mejor asignatura del estudiante
            mejor_asignatura = "Sin datos"
            mejor_nota = 0
            
            evaluaciones_por_asignatura = AlumnoEvaluacion.objects.filter(
                estudiante=estudiante
            ).select_related(
                'evaluacion__evaluacion_base__asignatura'
            ).values(
                'evaluacion__evaluacion_base__asignatura__nombre'
            ).annotate(
                promedio_asignatura=Avg('nota')
            ).order_by('-promedio_asignatura')
            
            if evaluaciones_por_asignatura:
                mejor_eval = evaluaciones_por_asignatura.first()
                mejor_asignatura = f"{mejor_eval['evaluacion__evaluacion_base__asignatura__nombre']} ({mejor_eval['promedio_asignatura']:.1f})"
                mejor_nota = mejor_eval['promedio_asignatura']
            
            # Determinar estado del estudiante
            if promedio_general >= 6.0 and porcentaje_asistencia >= 90:
                estado = "Excelente"
                estado_class = "success"
            elif promedio_general >= 5.0 and porcentaje_asistencia >= 80:
                estado = "Bueno"
                estado_class = "info"
            elif promedio_general >= 4.0 and porcentaje_asistencia >= 70:
                estado = "Regular"
                estado_class = "warning"
            else:
                estado = "En Riesgo"
                estado_class = "danger"
            
            ranking_estudiantes.append({
                'estudiante': estudiante,
                'promedio_general': promedio_general,
                'porcentaje_asistencia': porcentaje_asistencia,
                'mejor_asignatura': mejor_asignatura,
                'estado': estado,
                'estado_class': estado_class
            })
        
        # Ordenar por promedio general (descendente)
        ranking_estudiantes.sort(key=lambda x: x['promedio_general'], reverse=True)
        
        # Agregar posición al ranking
        for i, estudiante_data in enumerate(ranking_estudiantes, 1):
            estudiante_data['posicion'] = i
            
            # Determinar badge de posición
            if i == 1:
                estudiante_data['posicion_badge'] = "warning"  # Oro
            elif i == 2:
                estudiante_data['posicion_badge'] = "secondary"  # Plata
            elif i == 3:
                estudiante_data['posicion_badge'] = "info"  # Bronce
            else:
                estudiante_data['posicion_badge'] = "light"
        
        # Calcular datos de asistencia reales para cada estudiante
        asistencia_estudiantes = []
        for estudiante in estudiantes:
            # Obtener datos de asistencia del estudiante
            asistencia_data = get_asistencia_estudiante(estudiante.pk)
            
            # Calcular totales
            total_clases = sum(data['total'] for data in asistencia_data.values())
            total_presentes = sum(data['presentes'] for data in asistencia_data.values())
            total_ausentes = sum(data['ausentes'] for data in asistencia_data.values())
            total_justificadas = sum(data['justificados'] for data in asistencia_data.values())
            
            # Calcular tardanzas (simulado - en el modelo actual no hay tardanzas específicas)
            total_tardanzas = 0  # Por ahora 0, se puede implementar después
            
            # Calcular porcentaje
            porcentaje_asistencia = (total_presentes / total_clases * 100) if total_clases > 0 else 0
            
            # Determinar estado
            if porcentaje_asistencia >= 95:
                estado = "Excelente"
                estado_class = "success"
            elif porcentaje_asistencia >= 85:
                estado = "Bueno"
                estado_class = "info"
            elif porcentaje_asistencia >= 75:
                estado = "Regular"
                estado_class = "warning"
            else:
                estado = "En Riesgo"
                estado_class = "danger"
            
            asistencia_estudiantes.append({
                'estudiante': estudiante,
                'total_clases': total_clases,
                'presentes': total_presentes,
                'ausentes': total_ausentes,
                'justificados': total_justificadas,
                'tardanzas': total_tardanzas,
                'porcentaje_asistencia': porcentaje_asistencia,
                'estado': estado,
                'estado_class': estado_class
            })
        
        # Obtener comunicaciones específicas del curso
        comunicaciones_curso = Comunicacion.objects.filter(
            destinatarios_cursos=curso
        ).order_by('-fecha_envio')
        
        # Separar comunicaciones leídas y no leídas para el usuario actual
        comunicaciones_no_leidas = comunicaciones_curso.exclude(leido_por=request.user)[:10]
        comunicaciones_leidas = comunicaciones_curso.filter(leido_por=request.user)[:10]
        
        # Obtener las últimas 10 comunicaciones para la vista general
        comunicaciones_curso = comunicaciones_curso[:10]
        
        context = {
            'curso': curso,
            'estudiantes': estudiantes,
            'asignaturas': asignaturas,
            'profesor_jefe': profesor_jefe,
            'ranking_estudiantes': ranking_estudiantes,
            'asistencia_estudiantes': asistencia_estudiantes,
            'comunicaciones_curso': comunicaciones_curso,
            'comunicaciones_no_leidas': comunicaciones_no_leidas,
            'comunicaciones_leidas': comunicaciones_leidas
        }
        return render(request, 'teacher/curso_detalle.html', context)

@method_decorator(login_required, name='dispatch')
class AsignaturaDetalleView(View):
    def get(self, request, asignatura_id):
        asignatura = get_object_or_404(AsignaturaImpartida, id=asignatura_id)
        
        # Obtener estudiantes inscritos
        estudiantes = Estudiante.objects.filter(
            asignaturas_inscritas__asignatura_impartida=asignatura,
            asignaturas_inscritas__validada=True
        ).select_related('usuario')
        
        # Obtener clases de la asignatura
        clases = Clase.objects.filter(
            asignatura_impartida=asignatura
        ).order_by('fecha', 'horario')
        
        context = {
            'asignatura': asignatura,
            'estudiantes': estudiantes,
            'clases': clases
        }
        return render(request, 'teacher/asignatura_detalle.html', context)

@method_decorator(login_required, name='dispatch')
class AsignaturaDetalleEstudianteView(View):
    def get(self, request, asignatura_id):
        asignatura = get_object_or_404(AsignaturaImpartida, id=asignatura_id)
        
        # Verificar que el estudiante esté inscrito en esta asignatura
        if not hasattr(request.user.usuario, 'estudiante'):
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('estudiante_panel')
        
        estudiante = request.user.usuario.estudiante
        inscripcion = estudiante.asignaturas_inscritas.filter(
            asignatura_impartida=asignatura,
            validada=True
        ).first()
        
        if not inscripcion:
            messages.error(request, 'No estás inscrito en esta asignatura')
            return redirect('estudiante_panel')
        
        # Obtener clases de la asignatura
        clases = Clase.objects.filter(
            asignatura_impartida=asignatura
        ).order_by('fecha', 'horario')
        
        context = {
            'asignatura': asignatura,
            'clases': clases,
            'estudiante': estudiante
        }
        return render(request, 'student/asignatura_detalle.html', context)

@login_required
@require_http_methods(["POST"])
async def generar_reporte_ia(request):
    """Vista para generar reportes usando IA"""
    try:
        data = json.loads(request.body)
        curso_id = data.get('curso_id')
        tipo_reporte = data.get('tipo_reporte')
        
        # Verificar permisos
        curso = Curso.objects.get(id=curso_id)
        if not request.user.is_staff and not curso.tiene_acceso(request.user):
            raise PermissionDenied("No tiene permisos para acceder a este curso")
        
        # Determinar rol del usuario
        user_role = "ADMIN" if request.user.is_staff else "PROFESOR_JEFE" if curso.es_profesor_jefe(request.user) else "DOCENTE"
        
        # Inicializar servicio IA
        ia_service = IAService()
        
        # Generar reporte
        response = await ia_service.generate_response(
            template_name=f"reporte_{tipo_reporte}",
            user_role=user_role,
            user_id=request.user.id,
            curso_id=curso_id
        )
        
        return JsonResponse(response)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
async def generar_sugerencias_ia(request):
    """Vista para generar sugerencias de intervención usando IA"""
    try:
        data = json.loads(request.body)
        curso_id = data.get('curso_id')
        area = data.get('area')
        
        # Verificar permisos
        curso = Curso.objects.get(id=curso_id)
        if not request.user.is_staff and not curso.tiene_acceso(request.user):
            raise PermissionDenied("No tiene permisos para acceder a este curso")
        
        # Determinar rol del usuario
        user_role = "ADMIN" if request.user.is_staff else "PROFESOR_JEFE" if curso.es_profesor_jefe(request.user) else "DOCENTE"
        
        # Inicializar servicio IA
        ia_service = IAService()
        
        # Generar sugerencias
        response = await ia_service.generate_response(
            template_name="sugerencias_intervencion",
            user_role=user_role,
            user_id=request.user.id,
            curso_id=curso_id,
            area=area
        )
        
        return JsonResponse(response)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
async def generar_comunicado_ia(request):
    """Vista para generar comunicados usando IA"""
    try:
        data = json.loads(request.body)
        curso_id = data.get('curso_id')
        tipo_comunicado = data.get('tipo_comunicado')
        
        # Verificar permisos
        curso = Curso.objects.get(id=curso_id)
        if not request.user.is_staff and not curso.tiene_acceso(request.user):
            raise PermissionDenied("No tiene permisos para acceder a este curso")
        
        # Determinar rol del usuario
        user_role = "ADMIN" if request.user.is_staff else "PROFESOR_JEFE" if curso.es_profesor_jefe(request.user) else "DOCENTE"
        
        # Inicializar servicio IA
        ia_service = IAService()
        
        # Generar comunicado
        response = await ia_service.generate_response(
            template_name="comunicado",
            user_role=user_role,
            user_id=request.user.id,
            curso_id=curso_id,
            tipo_comunicado=tipo_comunicado
        )
        
        return JsonResponse(response)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# from django.shortcuts import render, redirect, get_object_or_404
# from django.views import View
# from django.contrib import messages
# from django.http import JsonResponse
# from Core.models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura
# from django.db.models import Count, Avg
# from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
# from django.utils import timezone
# from django.views.decorators.http import require_http_methods
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth import login, logout, authenticate
# from django.contrib.auth.hashers import make_password, check_password
# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from Core.servicios.repos import usuarios
# from Core.servicios.helpers import validadores, serializadores
# from Core.servicios.repos.cursos import get_estudiantes_por_curso

# @method_decorator(login_required, name='dispatch')
# class CursoView(View):
#     def get(self, request):
#         if not hasattr(request.user.usuario, 'estudiante'):
#             messages.error(request, 'No tienes permiso para acceder a esta página')
#             return redirect('home')
#         estudiantes = get_estudiantes_por_curso(request.user.usuario.estudiante.curso.id)
        
#         context = {
#             'estudiantes': estudiantes,
#             'curso': request.user.usuario.estudiante.curso
#         }
        
#         return render(request, 'student_panel.html', context)


