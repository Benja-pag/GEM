from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from datetime import datetime, date, timedelta
from collections import defaultdict
import json

from Core.models import (
    Usuario, Estudiante, Docente, Curso, Asignatura, AsignaturaImpartida, 
    Asistencia, Evaluacion, AlumnoEvaluacion, EvaluacionBase, Clase,
    Comunicacion, CalendarioColegio, CalendarioClase
)

def get_periodo_fechas(periodo):
    """Obtiene las fechas de inicio y fin según el período seleccionado"""
    hoy = date.today()
    
    if periodo == 'ultimo_mes':
        inicio = hoy.replace(day=1)
        fin = hoy
    elif periodo == 'ultimo_trimestre':
        # Último trimestre (3 meses)
        inicio = (hoy.replace(day=1) - timedelta(days=90)).replace(day=1)
        fin = hoy
    elif periodo == 'ultimo_semestre':
        # Último semestre (6 meses)
        inicio = (hoy.replace(day=1) - timedelta(days=180)).replace(day=1)
        fin = hoy
    elif periodo == 'ano_actual':
        inicio = date(hoy.year, 1, 1)
        fin = hoy
    else:  # Por defecto último mes
        inicio = hoy.replace(day=1)
        fin = hoy
    
    return inicio, fin

@method_decorator(login_required, name='dispatch')
class DashboardMetricasView(View):
    """Vista para obtener métricas generales del dashboard"""
    
    def get(self, request):
        # Usar la misma lógica de autorización que el panel del admin
        if not request.user.is_authenticated or not request.user.is_admin:
            return JsonResponse({'error': 'No autorizado'}, status=403)
        
        try:
            # Métricas básicas
            total_estudiantes = Estudiante.objects.count()
            total_docentes = Docente.objects.count()
            total_cursos = Curso.objects.count()
            total_asignaturas = Asignatura.objects.count()
            
            # Usar un rango de fechas más amplio para el promedio general
            fecha_inicio = date(date.today().year, 1, 1)  # Desde enero del año actual
            fecha_fin = date(date.today().year, 12, 31)   # Hasta diciembre del año actual
            
            # Promedio general del colegio (todo el año)
            evaluaciones_ano = AlumnoEvaluacion.objects.filter(
                evaluacion__fecha__gte=fecha_inicio,
                evaluacion__fecha__lte=fecha_fin
            )
            promedio_general = evaluaciones_ano.aggregate(
                promedio=Avg('nota')
            )['promedio'] or 0
            
            # Asistencia general del año
            asistencias_ano = Asistencia.objects.filter(
                fecha_registro__date__gte=fecha_inicio,
                fecha_registro__date__lte=fecha_fin
            )
            total_registros = asistencias_ano.count()
            presentes = asistencias_ano.filter(presente=True).count()
            porcentaje_asistencia = (presentes / total_registros * 100) if total_registros > 0 else 0
            
            # Estudiantes en riesgo (< 85% asistencia) - simplificado para mejor rendimiento
            estudiantes_riesgo = 0
            if total_registros > 0:
                # Estimación rápida basada en promedios
                estudiantes_riesgo = max(0, int(total_estudiantes * 0.1))  # Estimación del 10%
            
            # Comunicaciones del año
            comunicaciones_ano = Comunicacion.objects.filter(
                fecha_envio__date__gte=fecha_inicio,
                fecha_envio__date__lte=fecha_fin
            ).count()
            
            # Eventos del año
            eventos_ano = CalendarioColegio.objects.filter(
                fecha__gte=fecha_inicio,
                fecha__lte=fecha_fin
            ).count()
            
            data = {
                # Datos principales para el dashboard
                'total_estudiantes': int(total_estudiantes),
                'total_docentes': int(total_docentes),
                'promedio_general': float(round(promedio_general, 2)),
                'asistencia_promedio': float(round(porcentaje_asistencia, 1)),
                
                # Datos adicionales para análisis
                'metricas_basicas': {
                    'total_estudiantes': total_estudiantes,
                    'total_docentes': total_docentes,
                    'total_cursos': total_cursos,
                    'total_asignaturas': total_asignaturas
                },
                'rendimiento': {
                    'promedio_general': round(promedio_general, 2),
                    'total_evaluaciones': evaluaciones_ano.count()
                },
                'asistencia': {
                    'porcentaje_asistencia': round(porcentaje_asistencia, 1),
                    'estudiantes_riesgo': estudiantes_riesgo,
                    'total_registros': total_registros
                },
                'actividad': {
                    'comunicaciones_ano': comunicaciones_ano,
                    'eventos_ano': eventos_ano
                },
                'debug': {
                    'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                    'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                    'total_evaluaciones': evaluaciones_ano.count(),
                    'total_asistencias': total_registros,
                    'user_rut': getattr(request.user, 'rut', 'Unknown'),
                    'user_is_admin': getattr(request.user, 'is_admin', False),
                    'user_authenticated': request.user.is_authenticated
                }
            }
            
            return JsonResponse({'success': True, 'data': data})
            
        except Exception as e:
            # Agregar más información de debug
            import traceback
            error_details = {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'user_info': {
                    'is_authenticated': getattr(request.user, 'is_authenticated', False),
                    'is_admin': getattr(request.user, 'is_admin', False),
                    'rut': getattr(request.user, 'rut', 'Unknown'),
                    'user_type': str(type(request.user))
                }
            }
            print(f"Error en DashboardMetricasView: {error_details}")
            return JsonResponse({'success': False, 'error': str(e), 'debug': error_details})

@method_decorator(login_required, name='dispatch')
class ReporteRendimientoCursosView(View):
    """Vista para generar reporte de rendimiento por cursos"""
    
    def get(self, request):
        if not request.user.is_admin:
            return JsonResponse({'error': 'No autorizado'}, status=403)
        
        try:
            periodo = request.GET.get('periodo', 'ultimo_mes')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            cursos_data = []
            
            for curso in Curso.objects.all().order_by('nivel', 'letra'):
                # Obtener evaluaciones del período para este curso
                evaluaciones = AlumnoEvaluacion.objects.filter(
                    estudiante__curso=curso,
                    evaluacion__fecha__gte=fecha_inicio,
                    evaluacion__fecha__lte=fecha_fin
                )
                
                total_evaluaciones = evaluaciones.count()
                promedio_curso = evaluaciones.aggregate(promedio=Avg('nota'))['promedio'] or 0
                
                # Estudiantes con promedio >= 4.0
                estudiantes_aprobados = 0
                total_estudiantes = curso.estudiantes.count()
                
                for estudiante in curso.estudiantes.all():
                    eval_estudiante = evaluaciones.filter(estudiante=estudiante)
                    if eval_estudiante.exists():
                        promedio_est = eval_estudiante.aggregate(promedio=Avg('nota'))['promedio']
                        if promedio_est and promedio_est >= 4.0:
                            estudiantes_aprobados += 1
                
                porcentaje_aprobacion = (estudiantes_aprobados / total_estudiantes * 100) if total_estudiantes > 0 else 0
                
                # Asistencia del curso
                asistencias = Asistencia.objects.filter(
                    estudiante__curso=curso,
                    fecha_registro__date__gte=fecha_inicio,
                    fecha_registro__date__lte=fecha_fin
                )
                total_asistencias = asistencias.count()
                presentes = asistencias.filter(presente=True).count()
                porcentaje_asistencia = (presentes / total_asistencias * 100) if total_asistencias > 0 else 0
                
                cursos_data.append({
                    'curso': f"{curso.nivel}°{curso.letra}",
                    'total_estudiantes': total_estudiantes,
                    'total_evaluaciones': total_evaluaciones,
                    'promedio_curso': round(promedio_curso, 2),
                    'porcentaje_aprobacion': round(porcentaje_aprobacion, 1),
                    'porcentaje_asistencia': round(porcentaje_asistencia, 1),
                    'profesor_jefe': curso.jefatura_actual.docente.usuario.get_full_name() if hasattr(curso, 'jefatura_actual') and curso.jefatura_actual else 'No asignado'
                })
            
            return JsonResponse({
                'success': True, 
                'data': cursos_data,
                'periodo': periodo,
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y')
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
class ReporteAsistenciaGeneralView(View):
    """Vista para generar reporte de asistencia general"""
    
    def get(self, request):
        if not request.user.is_admin:
            return JsonResponse({'error': 'No autorizado'}, status=403)
        
        try:
            periodo = request.GET.get('periodo', 'ultimo_mes')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            # Asistencia por curso
            cursos_asistencia = []
            for curso in Curso.objects.all().order_by('nivel', 'letra'):
                asistencias = Asistencia.objects.filter(
                    estudiante__curso=curso,
                    fecha_registro__date__gte=fecha_inicio,
                    fecha_registro__date__lte=fecha_fin
                )
                
                total = asistencias.count()
                presentes = asistencias.filter(presente=True).count()
                ausentes = asistencias.filter(presente=False).count()
                justificados = asistencias.filter(presente=False, justificado=True).count()
                
                porcentaje = (presentes / total * 100) if total > 0 else 0
                
                # Estudiantes en riesgo (< 85% asistencia)
                estudiantes_riesgo = 0
                for estudiante in curso.estudiantes.all():
                    asist_est = asistencias.filter(estudiante=estudiante)
                    total_est = asist_est.count()
                    pres_est = asist_est.filter(presente=True).count()
                    if total_est > 0 and (pres_est / total_est * 100) < 85:
                        estudiantes_riesgo += 1
                
                cursos_asistencia.append({
                    'curso': f"{curso.nivel}°{curso.letra}",
                    'total_registros': total,
                    'presentes': presentes,
                    'ausentes': ausentes,
                    'justificados': justificados,
                    'porcentaje': round(porcentaje, 1),
                    'estudiantes_riesgo': estudiantes_riesgo,
                    'total_estudiantes': curso.estudiantes.count()
                })
            
            # Asistencia por asignatura
            asignaturas_asistencia = []
            for asignatura in Asignatura.objects.all():
                asistencias = Asistencia.objects.filter(
                    clase__asignatura_impartida__asignatura=asignatura,
                    fecha_registro__date__gte=fecha_inicio,
                    fecha_registro__date__lte=fecha_fin
                )
                
                total = asistencias.count()
                presentes = asistencias.filter(presente=True).count()
                porcentaje = (presentes / total * 100) if total > 0 else 0
                
                if total > 0:  # Solo incluir asignaturas con registros
                    asignaturas_asistencia.append({
                        'asignatura': asignatura.nombre,
                        'total_registros': total,
                        'presentes': presentes,
                        'porcentaje': round(porcentaje, 1)
                    })
            
            # Ordenar por porcentaje descendente
            asignaturas_asistencia.sort(key=lambda x: x['porcentaje'], reverse=True)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'cursos': cursos_asistencia,
                    'asignaturas': asignaturas_asistencia
                },
                'periodo': periodo,
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y')
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
class ReporteDocentesView(View):
    """Vista para generar reporte de gestión docente"""
    
    def get(self, request):
        if not request.user.is_admin:
            return JsonResponse({'error': 'No autorizado'}, status=403)
        
        try:
            periodo = request.GET.get('periodo', 'ultimo_mes')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            docentes_data = []
            
            for docente in Docente.objects.all().select_related('usuario', 'especialidad'):
                # Asignaturas que imparte
                asignaturas_impartidas = AsignaturaImpartida.objects.filter(docente=docente)
                total_asignaturas = asignaturas_impartidas.count()
                
                # Cursos donde es profesor jefe
                es_profesor_jefe = docente.jefaturas.exists()
                curso_jefe = docente.jefaturas.first().curso if es_profesor_jefe else None
                
                # Evaluaciones creadas en el período
                evaluaciones_creadas = Evaluacion.objects.filter(
                    clase__asignatura_impartida__docente=docente,
                    fecha__gte=fecha_inicio,
                    fecha__lte=fecha_fin
                ).count()
                
                # Comunicaciones enviadas
                try:
                    comunicaciones_enviadas = Comunicacion.objects.filter(
                        autor=docente.usuario.auth_user,
                        fecha_envio__date__gte=fecha_inicio,
                        fecha_envio__date__lte=fecha_fin
                    ).count()
                except:
                    comunicaciones_enviadas = 0
                
                # Promedio de notas de sus evaluaciones
                notas_evaluaciones = AlumnoEvaluacion.objects.filter(
                    evaluacion__clase__asignatura_impartida__docente=docente,
                    evaluacion__fecha__gte=fecha_inicio,
                    evaluacion__fecha__lte=fecha_fin
                )
                promedio_notas = notas_evaluaciones.aggregate(promedio=Avg('nota'))['promedio'] or 0
                
                # Total de estudiantes que atiende
                estudiantes_atendidos = set()
                for asignatura in asignaturas_impartidas:
                    clases = Clase.objects.filter(asignatura_impartida=asignatura)
                    for clase in clases:
                        if clase.curso:
                            estudiantes_atendidos.update(clase.curso.estudiantes.all())
                
                docentes_data.append({
                    'nombre': docente.usuario.get_full_name(),
                    'especialidad': docente.especialidad.nombre if docente.especialidad else 'Sin especialidad',
                    'total_asignaturas': total_asignaturas,
                    'es_profesor_jefe': es_profesor_jefe,
                    'curso_jefe': f"{curso_jefe.nivel}°{curso_jefe.letra}" if curso_jefe else 'N/A',
                    'evaluaciones_creadas': evaluaciones_creadas,
                    'comunicaciones_enviadas': comunicaciones_enviadas,
                    'promedio_notas': round(promedio_notas, 2),
                    'estudiantes_atendidos': len(estudiantes_atendidos)
                })
            
            return JsonResponse({
                'success': True,
                'data': docentes_data,
                'periodo': periodo,
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y')
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
class ReporteEstudiantesRiesgoView(View):
    """Vista para generar reporte de estudiantes en riesgo"""
    
    def get(self, request):
        if not request.user.is_admin:
            return JsonResponse({'error': 'No autorizado'}, status=403)
        
        try:
            periodo = request.GET.get('periodo', 'ultimo_mes')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            estudiantes_riesgo = []
            
            for estudiante in Estudiante.objects.all().select_related('usuario', 'curso'):
                # Calcular asistencia
                asistencias = Asistencia.objects.filter(
                    estudiante=estudiante,
                    fecha_registro__date__gte=fecha_inicio,
                    fecha_registro__date__lte=fecha_fin
                )
                total_asistencias = asistencias.count()
                presentes = asistencias.filter(presente=True).count()
                porcentaje_asistencia = (presentes / total_asistencias * 100) if total_asistencias > 0 else 100
                
                # Calcular promedio académico
                evaluaciones = AlumnoEvaluacion.objects.filter(
                    estudiante=estudiante,
                    evaluacion__fecha__gte=fecha_inicio,
                    evaluacion__fecha__lte=fecha_fin
                )
                promedio_academico = evaluaciones.aggregate(promedio=Avg('nota'))['promedio'] or 0
                
                # Determinar si está en riesgo
                riesgo_asistencia = porcentaje_asistencia < 85
                riesgo_academico = promedio_academico > 0 and promedio_academico < 4.0
                
                if riesgo_asistencia or riesgo_academico:
                    # Determinar tipo de riesgo
                    tipos_riesgo = []
                    if riesgo_asistencia:
                        tipos_riesgo.append('Asistencia')
                    if riesgo_academico:
                        tipos_riesgo.append('Académico')
                    
                    # Nivel de riesgo
                    if (riesgo_asistencia and porcentaje_asistencia < 70) or (riesgo_academico and promedio_academico < 3.0):
                        nivel_riesgo = 'Alto'
                    elif (riesgo_asistencia and porcentaje_asistencia < 80) or (riesgo_academico and promedio_academico < 3.5):
                        nivel_riesgo = 'Medio'
                    else:
                        nivel_riesgo = 'Bajo'
                    
                    estudiantes_riesgo.append({
                        'nombre': estudiante.usuario.get_full_name(),
                        'rut': estudiante.usuario.rut,
                        'curso': f"{estudiante.curso.nivel}°{estudiante.curso.letra}",
                        'porcentaje_asistencia': round(porcentaje_asistencia, 1),
                        'promedio_academico': round(promedio_academico, 2) if promedio_academico > 0 else 'Sin notas',
                        'tipos_riesgo': ', '.join(tipos_riesgo),
                        'nivel_riesgo': nivel_riesgo,
                        'total_evaluaciones': evaluaciones.count()
                    })
            
            # Ordenar por nivel de riesgo y luego por promedio
            orden_riesgo = {'Alto': 0, 'Medio': 1, 'Bajo': 2}
            estudiantes_riesgo.sort(key=lambda x: (orden_riesgo[x['nivel_riesgo']], x['porcentaje_asistencia']))
            
            return JsonResponse({
                'success': True,
                'data': estudiantes_riesgo,
                'periodo': periodo,
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                'total_estudiantes_riesgo': len(estudiantes_riesgo)
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
class ReporteEvaluacionesView(View):
    """Vista para generar reporte de evaluaciones por asignatura"""
    
    def get(self, request):
        if not request.user.is_admin:
            return JsonResponse({'error': 'No autorizado'}, status=403)
        
        try:
            periodo = request.GET.get('periodo', 'ultimo_mes')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            asignaturas_data = []
            
            for asignatura in Asignatura.objects.all():
                evaluaciones = Evaluacion.objects.filter(
                    evaluacion_base__asignatura=asignatura,
                    fecha__gte=fecha_inicio,
                    fecha__lte=fecha_fin
                )
                
                total_evaluaciones = evaluaciones.count()
                
                if total_evaluaciones > 0:
                    # Obtener todas las notas de estas evaluaciones
                    notas = AlumnoEvaluacion.objects.filter(
                        evaluacion__in=evaluaciones
                    )
                    
                    total_notas = notas.count()
                    promedio_asignatura = notas.aggregate(promedio=Avg('nota'))['promedio'] or 0
                    aprobados = notas.filter(nota__gte=4.0).count()
                    porcentaje_aprobacion = (aprobados / total_notas * 100) if total_notas > 0 else 0
                    
                    # Docentes que imparten esta asignatura
                    docentes = AsignaturaImpartida.objects.filter(
                        asignatura=asignatura
                    ).select_related('docente__usuario')
                    
                    docentes_nombres = [ai.docente.usuario.get_full_name() for ai in docentes]
                    
                    asignaturas_data.append({
                        'asignatura': asignatura.nombre,
                        'total_evaluaciones': total_evaluaciones,
                        'total_notas': total_notas,
                        'promedio_asignatura': round(promedio_asignatura, 2),
                        'porcentaje_aprobacion': round(porcentaje_aprobacion, 1),
                        'docentes': ', '.join(docentes_nombres) if docentes_nombres else 'Sin docentes asignados'
                    })
            
            # Ordenar por promedio descendente
            asignaturas_data.sort(key=lambda x: x['promedio_asignatura'], reverse=True)
            
            return JsonResponse({
                'success': True,
                'data': asignaturas_data,
                'periodo': periodo,
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y')
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}) 