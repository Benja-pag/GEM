from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from Core.models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura, AsignaturaImpartida, Curso, ProfesorJefe, Evaluacion, AlumnoEvaluacion, EvaluacionBase
from django.db.models import Count, Avg
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.db import transaction
from Core.servicios.repos import usuarios
from Core.servicios.helpers import validadores, serializadores
from datetime import date, timedelta

def get_evaluaciones_docente(docente_id):
    """
    Obtiene todas las evaluaciones que ha creado el docente
    """
    evaluaciones = Evaluacion.objects.filter(
        clase__asignatura_impartida__docente_id=docente_id
    ).select_related(
        'evaluacion_base__asignatura',
        'clase__asignatura_impartida__asignatura',
        'clase__curso'
    ).order_by(
        'clase__asignatura_impartida__asignatura__nombre',
        'evaluacion_base__nombre',
        'fecha'
    )
    
    # Agrupar por asignatura y tipo de evaluación para evitar duplicados
    evaluaciones_por_asignatura = {}
    for evaluacion in evaluaciones:
        asignatura_nombre = evaluacion.evaluacion_base.asignatura.nombre
        tipo_evaluacion = evaluacion.evaluacion_base.nombre
        
        if asignatura_nombre not in evaluaciones_por_asignatura:
            evaluaciones_por_asignatura[asignatura_nombre] = {}
        
        # Solo agregar si no existe ya este tipo de evaluación para esta asignatura
        if tipo_evaluacion not in evaluaciones_por_asignatura[asignatura_nombre]:
            # Calcular estadísticas de la evaluación
            notas = AlumnoEvaluacion.objects.filter(evaluacion=evaluacion)
            promedio = notas.aggregate(promedio=Avg('nota'))['promedio'] if notas.exists() else 0
            total_estudiantes = notas.count()
            aprobados = notas.filter(nota__gte=4.0).count()
            porcentaje_aprobacion = (aprobados / total_estudiantes * 100) if total_estudiantes > 0 else 0
            
            evaluaciones_por_asignatura[asignatura_nombre][tipo_evaluacion] = {
                'id': evaluacion.id,
                'nombre': evaluacion.evaluacion_base.nombre,
                'fecha': evaluacion.fecha,
                'ponderacion': evaluacion.evaluacion_base.ponderacion,
                'curso': evaluacion.clase.curso,
                'promedio': promedio,
                'total_estudiantes': total_estudiantes,
                'aprobados': aprobados,
                'porcentaje_aprobacion': porcentaje_aprobacion,
                'estado': 'Calificada' if total_estudiantes > 0 else 'Pendiente'
            }
    
    # Convertir el diccionario anidado a una lista plana para cada asignatura
    resultado = {}
    for asignatura, evaluaciones in evaluaciones_por_asignatura.items():
        resultado[asignatura] = list(evaluaciones.values())
    
    return resultado

def get_estadisticas_docente(docente_id):
    """
    Obtiene estadísticas generales del docente
    """
    evaluaciones = Evaluacion.objects.filter(
        clase__asignatura_impartida__docente_id=docente_id
    )
    
    total_evaluaciones = evaluaciones.count()
    evaluaciones_calificadas = 0
    promedio_general = 0
    total_notas = 0
    
    for evaluacion in evaluaciones:
        notas = AlumnoEvaluacion.objects.filter(evaluacion=evaluacion)
        if notas.exists():
            evaluaciones_calificadas += 1
            promedio_eval = notas.aggregate(promedio=Avg('nota'))['promedio']
            total_notas += promedio_eval
    
    if evaluaciones_calificadas > 0:
        promedio_general = total_notas / evaluaciones_calificadas
    
    return {
        'total_evaluaciones': total_evaluaciones,
        'evaluaciones_calificadas': evaluaciones_calificadas,
        'promedio_general': promedio_general
    }

def get_estadisticas_asistencia_docente(docente_id):
    """
    Obtiene estadísticas de asistencia del docente para el mes actual
    """
    # Obtener fechas del mes actual
    hoy = date.today()
    primer_dia = date(hoy.year, hoy.month, 1)
    
    # Si estamos en el primer día del mes, usar el mes anterior
    if hoy.day <= 5:
        primer_dia = primer_dia - timedelta(days=30)
        primer_dia = date(primer_dia.year, primer_dia.month, 1)
    
    # Obtener el último día del mes
    if primer_dia.month == 12:
        ultimo_dia = date(primer_dia.year + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(primer_dia.year, primer_dia.month + 1, 1) - timedelta(days=1)
    
    # Obtener asistencias de las clases del docente para el mes
    asistencias = Asistencia.objects.filter(
        clase__asignatura_impartida__docente_id=docente_id,
        fecha_registro__date__gte=primer_dia,
        fecha_registro__date__lte=ultimo_dia
    ).select_related('clase__asignatura_impartida__asignatura', 'clase__curso')
    
    # Agrupar por asignatura y curso
    estadisticas = {}
    for asistencia in asistencias:
        asignatura_nombre = asistencia.clase.asignatura_impartida.asignatura.nombre
        curso_nombre = str(asistencia.clase.curso)
        clave = f"{asignatura_nombre} - {curso_nombre}"
        
        if clave not in estadisticas:
            estadisticas[clave] = {
                'asignatura': asignatura_nombre,
                'curso': curso_nombre,
                'total': 0,
                'presentes': 0,
                'ausentes': 0,
                'justificados': 0,
                'porcentaje': 0.0
            }
        
        estadisticas[clave]['total'] += 1
        if asistencia.presente:
            estadisticas[clave]['presentes'] += 1
        else:
            estadisticas[clave]['ausentes'] += 1
            if asistencia.justificado:
                estadisticas[clave]['justificados'] += 1
    
    # Calcular porcentajes
    for stats in estadisticas.values():
        if stats['total'] > 0:
            stats['porcentaje'] = (stats['presentes'] / stats['total']) * 100
    
    return estadisticas

@method_decorator(login_required, name='dispatch')
class ProfesorPanelView(View):
    def get(self, request):
        if not hasattr(request.user.usuario, 'docente'):
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        
        docente = request.user.usuario.docente
        
        # Obtener cursos donde el docente es profesor jefe
        cursos_profesor_jefe = Curso.objects.filter(
            jefatura_actual__docente=docente
        ).select_related('jefatura_actual__docente__usuario').annotate(
            total_estudiantes=Count('estudiantes')
        )
        
        # Obtener asignaturas que imparte el docente
        asignaturas = AsignaturaImpartida.objects.filter(
            docente=docente
        ).select_related(
            'asignatura',
            'docente__usuario'
        ).prefetch_related('clases')
        
        # Obtener evaluaciones del docente
        evaluaciones_docente = get_evaluaciones_docente(docente.pk)
        estadisticas_docente = get_estadisticas_docente(docente.pk)
        estadisticas_asistencia = get_estadisticas_asistencia_docente(docente.pk)
        
        context = {
            'cursos_profesor_jefe': cursos_profesor_jefe,
            'asignaturas': asignaturas,
            'evaluaciones_docente': evaluaciones_docente,
            'estadisticas_docente': estadisticas_docente,
            'estadisticas_asistencia': estadisticas_asistencia
        }
        return render(request, 'teacher_panel.html', context)

@method_decorator(login_required, name='dispatch')
class ProfesorPanelModularView(View):
    def get(self, request):
        if not hasattr(request.user.usuario, 'docente'):
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        
        docente = request.user.usuario.docente
        
        # Obtener cursos donde el docente es profesor jefe
        cursos_profesor_jefe = Curso.objects.filter(
            jefatura_actual__docente=docente
        ).select_related('jefatura_actual__docente__usuario').annotate(
            total_estudiantes=Count('estudiantes')
        )
        
        # Obtener asignaturas que imparte el docente
        asignaturas = AsignaturaImpartida.objects.filter(
            docente=docente
        ).select_related(
            'asignatura',
            'docente__usuario'
        ).prefetch_related('clases')
        
        # Obtener evaluaciones del docente
        evaluaciones_docente = get_evaluaciones_docente(docente.pk)
        estadisticas_docente = get_estadisticas_docente(docente.pk)
        estadisticas_asistencia = get_estadisticas_asistencia_docente(docente.pk)
        
        context = {
            'cursos_profesor_jefe': cursos_profesor_jefe,
            'asignaturas': asignaturas,
            'evaluaciones_docente': evaluaciones_docente,
            'estadisticas_docente': estadisticas_docente,
            'estadisticas_asistencia': estadisticas_asistencia
        }
        return render(request, 'teacher_panel_modular.html', context)

