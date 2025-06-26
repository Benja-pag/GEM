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
class ReporteRendimientoCursosViewSimple(View):
    """Vista simplificada para generar reporte de rendimiento por cursos"""
    
    def get(self, request):
        try:
            periodo = request.GET.get('periodo', 'ultimo_mes')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            cursos_data = []
            
            # Obtener cursos de forma más simple
            cursos = Curso.objects.all().order_by('nivel', 'letra')
            
            for curso in cursos:
                try:
                    # Datos básicos del curso
                    total_estudiantes = curso.estudiantes.count()
                    
                    # Obtener TODAS las evaluaciones de los estudiantes del curso en el período
                    evaluaciones_estudiantes = []
                    total_evaluaciones = 0
                    suma_notas = 0
                    estudiantes_aprobados = 0
                    
                    for estudiante in curso.estudiantes.all():
                        # Obtener todas las evaluaciones del estudiante en el período
                        eval_estudiante = AlumnoEvaluacion.objects.filter(
                            estudiante=estudiante,
                            evaluacion__fecha__gte=fecha_inicio,
                            evaluacion__fecha__lte=fecha_fin
                        )
                        
                        if eval_estudiante.exists():
                            # Calcular promedio del estudiante
                            promedio_est = eval_estudiante.aggregate(promedio=Avg('nota'))['promedio']
                            if promedio_est:
                                suma_notas += promedio_est
                                if promedio_est >= 4.0:
                                    estudiantes_aprobados += 1
                            
                            total_evaluaciones += eval_estudiante.count()
                            evaluaciones_estudiantes.extend(list(eval_estudiante))
                    
                    # Calcular promedio general del curso
                    promedio_curso = suma_notas / total_estudiantes if total_estudiantes > 0 else 0
                    
                    # Calcular porcentaje de aprobación
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
                    
                    # Profesor jefe
                    profesor_jefe = 'No asignado'
                    try:
                        if hasattr(curso, 'jefatura_actual') and curso.jefatura_actual:
                            profesor_jefe = curso.jefatura_actual.docente.usuario.get_full_name()
                    except:
                        profesor_jefe = 'No asignado'
                    
                    cursos_data.append({
                        'curso': f"{curso.nivel}°{curso.letra}",
                        'total_estudiantes': total_estudiantes,
                        'total_evaluaciones': total_evaluaciones,
                        'promedio_curso': round(promedio_curso, 2),
                        'porcentaje_aprobacion': round(porcentaje_aprobacion, 1),
                        'porcentaje_asistencia': round(porcentaje_asistencia, 1),
                        'profesor_jefe': profesor_jefe,
                        'debug_info': f"Est: {total_estudiantes}, Evals: {total_evaluaciones}, Aprobados: {estudiantes_aprobados}"
                    })
                    
                except Exception as e:
                    # Si hay error con un curso específico, continuar con el siguiente
                    continue
            
            return JsonResponse({
                'success': True, 
                'data': cursos_data,
                'periodo': periodo,
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y')
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error en reporte de rendimiento: {str(e)}'})

@method_decorator(login_required, name='dispatch')
class ReporteDocentesViewSimple(View):
    """Vista simplificada para generar reporte de gestión docente"""
    
    def get(self, request):
        try:
            periodo = request.GET.get('periodo', 'ultimo_mes')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            docentes_data = []
            
            for docente in Docente.objects.all():
                try:
                    # Asignaturas que imparte
                    asignaturas_impartidas = AsignaturaImpartida.objects.filter(docente=docente)
                    total_asignaturas = asignaturas_impartidas.count()
                    
                    # Es profesor jefe?
                    es_profesor_jefe = False
                    curso_jefe = 'N/A'
                    try:
                        if hasattr(docente, 'jefaturas') and docente.jefaturas.exists():
                            es_profesor_jefe = True
                            jefatura = docente.jefaturas.first()
                            if jefatura and jefatura.curso:
                                curso_jefe = f"{jefatura.curso.nivel}°{jefatura.curso.letra}"
                    except:
                        pass
                    
                    # Evaluaciones creadas
                    evaluaciones_creadas = 0
                    try:
                        evaluaciones_creadas = Evaluacion.objects.filter(
                            clase__asignatura_impartida__docente=docente,
                            fecha__gte=fecha_inicio,
                            fecha__lte=fecha_fin
                        ).count()
                    except:
                        pass
                    
                    # Comunicaciones enviadas
                    comunicaciones_enviadas = 0
                    try:
                        if hasattr(docente.usuario, 'auth_user'):
                            comunicaciones_enviadas = Comunicacion.objects.filter(
                                autor=docente.usuario.auth_user,
                                fecha_envio__date__gte=fecha_inicio,
                                fecha_envio__date__lte=fecha_fin
                            ).count()
                    except:
                        pass
                    
                    # Promedio de notas
                    promedio_notas = 0
                    try:
                        notas_evaluaciones = AlumnoEvaluacion.objects.filter(
                            evaluacion__clase__asignatura_impartida__docente=docente,
                            evaluacion__fecha__gte=fecha_inicio,
                            evaluacion__fecha__lte=fecha_fin
                        )
                        if notas_evaluaciones.exists():
                            promedio_notas = notas_evaluaciones.aggregate(promedio=Avg('nota'))['promedio'] or 0
                    except:
                        pass
                    
                    docentes_data.append({
                        'nombre': docente.usuario.get_full_name(),
                        'especialidad': docente.especialidad.nombre if docente.especialidad else 'Sin especialidad',
                        'total_asignaturas': total_asignaturas,
                        'es_profesor_jefe': es_profesor_jefe,
                        'curso_jefe': curso_jefe,
                        'evaluaciones_creadas': evaluaciones_creadas,
                        'comunicaciones_enviadas': comunicaciones_enviadas,
                        'promedio_notas': round(promedio_notas, 2),
                        'estudiantes_atendidos': 0  # Simplificado por ahora
                    })
                    
                except Exception as e:
                    # Si hay error con un docente específico, continuar
                    continue
            
            return JsonResponse({
                'success': True,
                'data': docentes_data,
                'periodo': periodo,
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y')
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error en reporte de docentes: {str(e)}'})

@method_decorator(login_required, name='dispatch')
class ReporteEstudiantesRiesgoViewSimple(View):
    """Vista simplificada para generar reporte de estudiantes en riesgo"""
    
    def get(self, request):
        try:
            periodo = request.GET.get('periodo', 'ultimo_mes')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            estudiantes_riesgo = []
            
            for estudiante in Estudiante.objects.all():
                try:
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
                    promedio_academico = 0
                    if evaluaciones.exists():
                        promedio_academico = evaluaciones.aggregate(promedio=Avg('nota'))['promedio'] or 0
                    
                    # Determinar si está en riesgo
                    riesgo_asistencia = porcentaje_asistencia < 85
                    riesgo_academico = promedio_academico > 0 and promedio_academico < 4.0
                    
                    if riesgo_asistencia or riesgo_academico:
                        # Tipos de riesgo
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
                        
                except Exception as e:
                    # Si hay error con un estudiante específico, continuar
                    continue
            
            # Ordenar por nivel de riesgo
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
            return JsonResponse({'success': False, 'error': f'Error en reporte de estudiantes en riesgo: {str(e)}'}) 