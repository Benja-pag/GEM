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
        # Expandir a los últimos 3 meses para capturar más datos
        inicio = (hoy.replace(day=1) - timedelta(days=90)).replace(day=1)
        fin = hoy + timedelta(days=30)  # Incluir fechas futuras próximas
    elif periodo == 'ultimo_trimestre':
        # Último trimestre (3 meses)
        inicio = (hoy.replace(day=1) - timedelta(days=120)).replace(day=1)
        fin = hoy + timedelta(days=30)
    elif periodo == 'ultimo_semestre':
        # Último semestre (6 meses)
        inicio = (hoy.replace(day=1) - timedelta(days=180)).replace(day=1)
        fin = hoy + timedelta(days=30)
    elif periodo == 'ano_actual':
        inicio = date(hoy.year, 1, 1)
        fin = date(hoy.year, 12, 31)  # Todo el año
    else:  # Por defecto año actual completo
        inicio = date(hoy.year, 1, 1)
        fin = date(hoy.year, 12, 31)
    
    return inicio, fin

@method_decorator(login_required, name='dispatch')
class ReporteRendimientoCursosViewSimple(View):
    """Vista simplificada para generar reporte de rendimiento por cursos"""
    
    def get(self, request):
        # Usar la misma lógica de autorización que el panel del admin
        if not request.user.is_authenticated or not request.user.is_admin:
            return JsonResponse({'error': 'No autorizado'}, status=403)
            
        try:
            periodo = request.GET.get('periodo', 'ano_actual')  # Cambiar default a año actual
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            cursos_data = []
            
            # Obtener cursos de forma más simple
            cursos = Curso.objects.all().order_by('nivel', 'letra')
            
            for curso in cursos:
                try:
                    # Datos básicos del curso
                    total_estudiantes = curso.estudiantes.count()
                    
                    if total_estudiantes == 0:
                        # Curso sin estudiantes
                        cursos_data.append({
                            'curso': f"{curso.nivel}°{curso.letra}",
                            'total_estudiantes': 0,
                            'total_evaluaciones': 0,
                            'promedio_curso': 0.0,
                            'porcentaje_aprobacion': 0.0,
                            'porcentaje_asistencia': 0.0,
                            'profesor_jefe': 'No asignado',
                            'estudiantes_con_notas': 0,
                            'estudiantes_aprobados': 0,
                            'estado': 'N/A',
                            'estado_clase': 'secondary'
                        })
                        continue
                    
                    # Obtener TODAS las evaluaciones de los estudiantes del curso en el período
                    total_evaluaciones = 0
                    suma_promedios_estudiantes = 0
                    estudiantes_con_notas = 0
                    estudiantes_aprobados = 0
                    
                    for estudiante in curso.estudiantes.all():
                        # Obtener todas las evaluaciones del estudiante en el período
                        eval_estudiante = AlumnoEvaluacion.objects.filter(
                            estudiante=estudiante,
                            evaluacion__fecha__gte=fecha_inicio,
                            evaluacion__fecha__lte=fecha_fin
                        )
                        
                        total_evaluaciones += eval_estudiante.count()
                        
                        if eval_estudiante.exists():
                            # Calcular promedio del estudiante
                            promedio_est = eval_estudiante.aggregate(promedio=Avg('nota'))['promedio']
                            if promedio_est is not None:
                                suma_promedios_estudiantes += promedio_est
                                estudiantes_con_notas += 1
                                if promedio_est >= 4.0:
                                    estudiantes_aprobados += 1
                    
                    # Calcular promedio general del curso (promedio de promedios de estudiantes)
                    promedio_curso = suma_promedios_estudiantes / estudiantes_con_notas if estudiantes_con_notas > 0 else 0
                    
                    # Calcular porcentaje de aprobación (sobre estudiantes con notas)
                    porcentaje_aprobacion = (estudiantes_aprobados / estudiantes_con_notas * 100) if estudiantes_con_notas > 0 else 0
                    
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
                    
                    # Determinar estado basado en asistencia
                    if porcentaje_asistencia < 83:
                        estado = "Crítico"
                        estado_clase = "danger"
                    elif porcentaje_asistencia < 85:
                        estado = "Regular"
                        estado_clase = "warning"
                    else:
                        estado = "Bueno"
                        estado_clase = "success"
                    
                    cursos_data.append({
                        'curso': f"{curso.nivel}°{curso.letra}",
                        'total_estudiantes': int(total_estudiantes),
                        'total_evaluaciones': int(total_evaluaciones),
                        'promedio_curso': float(round(promedio_curso, 2)),
                        'porcentaje_aprobacion': float(round(porcentaje_aprobacion, 1)),
                        'porcentaje_asistencia': float(round(porcentaje_asistencia, 1)),
                        'profesor_jefe': profesor_jefe,
                        'estudiantes_con_notas': int(estudiantes_con_notas),
                        'estudiantes_aprobados': int(estudiantes_aprobados),
                        'estado': estado,
                        'estado_clase': estado_clase
                    })
                    
                except Exception as e:
                    print(f"Error procesando curso {curso.nivel}°{curso.letra}: {str(e)}")
                    # Si hay error con un curso específico, continuar con el siguiente
                    continue
            
            return JsonResponse({
                'success': True, 
                'data': cursos_data,
                'periodo': periodo,
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                'debug': f"Período: {periodo}, Rango: {fecha_inicio} a {fecha_fin}"
            })
            
        except Exception as e:
            print(f"Error en reporte de rendimiento: {str(e)}")
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
        # Usar la misma lógica de autorización que el panel del admin
        if not request.user.is_authenticated or not request.user.is_admin:
            return JsonResponse({'error': 'No autorizado'}, status=403)
            
        try:
            periodo = request.GET.get('periodo', 'ano_actual')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            estudiantes_riesgo_notas = []
            estudiantes_riesgo_asistencia = []
            
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
                    
                    # Estudiante en riesgo académico
                    if riesgo_academico:
                        estudiantes_riesgo_notas.append({
                            'nombre': estudiante.usuario.get_full_name(),
                            'rut': estudiante.usuario.rut,
                            'curso': f"{estudiante.curso.nivel}°{estudiante.curso.letra}",
                            'promedio': float(round(promedio_academico, 2)),
                            'total_evaluaciones': int(evaluaciones.count())
                        })
                    
                    # Estudiante en riesgo de asistencia
                    if riesgo_asistencia:
                        estudiantes_riesgo_asistencia.append({
                            'nombre': estudiante.usuario.get_full_name(),
                            'rut': estudiante.usuario.rut,
                            'curso': f"{estudiante.curso.nivel}°{estudiante.curso.letra}",
                            'asistencia': float(round(porcentaje_asistencia, 1)),
                            'total_asistencias': int(total_asistencias)
                        })
                        
                except Exception as e:
                    print(f"Error procesando estudiante {estudiante.usuario.get_full_name()}: {str(e)}")
                    # Si hay error con un estudiante específico, continuar
                    continue
            
            # Ordenar por promedio/asistencia
            estudiantes_riesgo_notas.sort(key=lambda x: x['promedio'])
            estudiantes_riesgo_asistencia.sort(key=lambda x: x['asistencia'])
            
            return JsonResponse({
                'success': True,
                'data': {
                    'riesgo_notas': estudiantes_riesgo_notas,
                    'riesgo_asistencia': estudiantes_riesgo_asistencia
                },
                'periodo': periodo,
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                'total_riesgo_notas': len(estudiantes_riesgo_notas),
                'total_riesgo_asistencia': len(estudiantes_riesgo_asistencia)
            })
            
        except Exception as e:
            print(f"Error en reporte de estudiantes en riesgo: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Error en reporte de estudiantes en riesgo: {str(e)}'})

@method_decorator(login_required, name='dispatch')
class ReporteAsistenciaGeneralViewSimple(View):
    """Vista simplificada para generar reporte de asistencia general por cursos"""
    
    def get(self, request):
        # Usar la misma lógica de autorización que el panel del admin
        if not request.user.is_authenticated or not request.user.is_admin:
            return JsonResponse({'error': 'No autorizado'}, status=403)
        
        try:
            periodo = request.GET.get('periodo', 'ano_actual')  # Cambiar a año actual por defecto
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            # Datos de asistencia por curso
            cursos_asistencia = []
            cursos = Curso.objects.all().order_by('nivel', 'letra')
            
            for curso in cursos:
                # Obtener estudiantes del curso
                estudiantes = curso.estudiantes.all()
                total_estudiantes = estudiantes.count()
                
                if total_estudiantes == 0:
                    # Curso sin estudiantes
                    cursos_asistencia.append({
                        'curso': f"{curso.nivel}°{curso.letra}",
                        'total_estudiantes': 0,
                        'total_registros': 0,
                        'presentes': 0,
                        'ausentes': 0,
                        'justificados': 0,
                        'porcentaje_asistencia': 0.0,
                        'estudiantes_riesgo': 0,
                        'estado': 'N/A',
                        'estado_clase': 'secondary'
                    })
                    continue
                
                # Obtener asistencias del curso
                asistencias = Asistencia.objects.filter(
                    estudiante__curso=curso,
                    fecha_registro__date__gte=fecha_inicio,
                    fecha_registro__date__lte=fecha_fin
                )
                
                total_registros = asistencias.count()
                presentes = asistencias.filter(presente=True).count()
                ausentes = asistencias.filter(presente=False).count()
                justificados = asistencias.filter(presente=False, justificado=True).count()
                
                porcentaje_asistencia = (presentes / total_registros * 100) if total_registros > 0 else 0
                
                # Calcular estudiantes en riesgo (< 85% asistencia individual)
                estudiantes_riesgo = 0
                for estudiante in estudiantes:
                    asist_estudiante = asistencias.filter(estudiante=estudiante)
                    total_est = asist_estudiante.count()
                    pres_est = asist_estudiante.filter(presente=True).count()
                    if total_est > 0 and (pres_est / total_est * 100) < 85:
                        estudiantes_riesgo += 1
                
                # Determinar estado basado en porcentaje de asistencia del curso
                if porcentaje_asistencia < 83:
                    estado = "Crítico"
                    estado_clase = "danger"
                elif porcentaje_asistencia < 85:
                    estado = "Regular"
                    estado_clase = "warning"
                else:
                    estado = "Bueno"
                    estado_clase = "success"
                
                cursos_asistencia.append({
                    'curso': f"{curso.nivel}°{curso.letra}",
                    'total_estudiantes': int(total_estudiantes),
                    'total_registros': int(total_registros),
                    'presentes': int(presentes),
                    'ausentes': int(ausentes),
                    'justificados': int(justificados),
                    'porcentaje_asistencia': float(round(porcentaje_asistencia, 1)),
                    'estudiantes_riesgo': int(estudiantes_riesgo),
                    'estado': estado,
                    'estado_clase': estado_clase
                })
            
            return JsonResponse({
                'success': True,
                'data': cursos_asistencia,
                'periodo': periodo,
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                'total_cursos': len([c for c in cursos_asistencia if c['total_estudiantes'] > 0])
            })
            
        except Exception as e:
            print(f"Error en reporte de asistencia general: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Error en reporte de asistencia general: {str(e)}'})

@method_decorator(login_required, name='dispatch')
class ReporteAsistenciaEstudianteViewSimple(View):
    """Vista para generar reporte de asistencia de un estudiante específico"""
    
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            return JsonResponse({'error': 'No autorizado'}, status=403)
        
        try:
            estudiante_id = request.GET.get('estudiante_id')
            if not estudiante_id:
                return JsonResponse({'success': False, 'error': 'ID de estudiante requerido'})
            
            periodo = request.GET.get('periodo', 'ano_actual')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            try:
                estudiante = Estudiante.objects.get(id=estudiante_id)
            except Estudiante.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Estudiante no encontrado'})
            
            # Obtener asistencias del estudiante
            asistencias = Asistencia.objects.filter(
                estudiante=estudiante,
                fecha_registro__date__gte=fecha_inicio,
                fecha_registro__date__lte=fecha_fin
            ).order_by('-fecha_registro')
            
            # Estadísticas generales
            total_registros = asistencias.count()
            presentes = asistencias.filter(presente=True).count()
            ausentes = asistencias.filter(presente=False).count()
            justificados = asistencias.filter(presente=False, justificado=True).count()
            injustificados = ausentes - justificados
            
            porcentaje_asistencia = (presentes / total_registros * 100) if total_registros > 0 else 100
            
            # Determinar estado
            if porcentaje_asistencia < 70:
                estado = "Crítico"
                estado_clase = "danger"
            elif porcentaje_asistencia < 85:
                estado = "En Riesgo"
                estado_clase = "warning"
            else:
                estado = "Bueno"
                estado_clase = "success"
            
            # Detalle por asignatura
            asignaturas_detalle = []
            asignaturas = set(asistencias.values_list('asignatura__nombre', flat=True))
            
            for asignatura_nombre in asignaturas:
                asist_asignatura = asistencias.filter(asignatura__nombre=asignatura_nombre)
                total_asig = asist_asignatura.count()
                pres_asig = asist_asignatura.filter(presente=True).count()
                aus_asig = asist_asignatura.filter(presente=False).count()
                just_asig = asist_asignatura.filter(presente=False, justificado=True).count()
                
                porcentaje_asig = (pres_asig / total_asig * 100) if total_asig > 0 else 100
                
                asignaturas_detalle.append({
                    'asignatura': asignatura_nombre,
                    'total_clases': int(total_asig),
                    'presentes': int(pres_asig),
                    'ausentes': int(aus_asig),
                    'justificados': int(just_asig),
                    'porcentaje': float(round(porcentaje_asig, 1))
                })
            
            # Ordenar por porcentaje de asistencia
            asignaturas_detalle.sort(key=lambda x: x['porcentaje'])
            
            # Historial reciente (últimas 30 clases)
            historial_reciente = []
            asistencias_recientes = asistencias[:30]
            
            for asistencia in asistencias_recientes:
                historial_reciente.append({
                    'fecha': asistencia.fecha_registro.strftime('%d/%m/%Y'),
                    'asignatura': asistencia.asignatura.nombre,
                    'presente': asistencia.presente,
                    'justificado': asistencia.justificado if not asistencia.presente else None,
                    'observaciones': asistencia.observaciones or ''
                })
            
            return JsonResponse({
                'success': True,
                'data': {
                    'estudiante': {
                        'nombre': estudiante.usuario.get_full_name(),
                        'rut': estudiante.usuario.rut,
                        'curso': f"{estudiante.curso.nivel}°{estudiante.curso.letra}"
                    },
                    'estadisticas': {
                        'total_registros': int(total_registros),
                        'presentes': int(presentes),
                        'ausentes': int(ausentes),
                        'justificados': int(justificados),
                        'injustificados': int(injustificados),
                        'porcentaje_asistencia': float(round(porcentaje_asistencia, 1)),
                        'estado': estado,
                        'estado_clase': estado_clase
                    },
                    'asignaturas': asignaturas_detalle,
                    'historial': historial_reciente
                },
                'periodo': periodo,
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y')
            })
            
        except Exception as e:
            print(f"Error en reporte de asistencia de estudiante: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Error en reporte de asistencia de estudiante: {str(e)}'})

@method_decorator(login_required, name='dispatch')
class ReporteAsistenciaCursoViewSimple(View):
    """Vista para generar reporte de asistencia de un curso específico"""
    
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            return JsonResponse({'error': 'No autorizado'}, status=403)
        
        try:
            curso_id = request.GET.get('curso_id')
            if not curso_id:
                return JsonResponse({'success': False, 'error': 'ID de curso requerido'})
            
            periodo = request.GET.get('periodo', 'ano_actual')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            try:
                curso = Curso.objects.get(id=curso_id)
            except Curso.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Curso no encontrado'})
            
            # Obtener estudiantes del curso
            estudiantes = curso.estudiantes.all().order_by('usuario__apellido_paterno', 'usuario__nombre')
            
            if not estudiantes.exists():
                return JsonResponse({
                    'success': True,
                    'data': {
                        'curso': {
                            'nombre': f"{curso.nivel}°{curso.letra}",
                            'total_estudiantes': 0
                        },
                        'estadisticas': {
                            'total_registros': 0,
                            'promedio_asistencia': 0.0,
                            'estudiantes_criticos': 0,
                            'estudiantes_riesgo': 0,
                            'estudiantes_buenos': 0
                        },
                        'estudiantes': [],
                        'asignaturas': []
                    },
                    'periodo': periodo,
                    'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                    'fecha_fin': fecha_fin.strftime('%d/%m/%Y')
                })
            
            # Estadísticas por estudiante
            estudiantes_detalle = []
            total_asistencia_curso = 0
            estudiantes_criticos = 0
            estudiantes_riesgo = 0
            estudiantes_buenos = 0
            
            for estudiante in estudiantes:
                asistencias = Asistencia.objects.filter(
                    estudiante=estudiante,
                    fecha_registro__date__gte=fecha_inicio,
                    fecha_registro__date__lte=fecha_fin
                )
                
                total_reg = asistencias.count()
                presentes = asistencias.filter(presente=True).count()
                ausentes = asistencias.filter(presente=False).count()
                justificados = asistencias.filter(presente=False, justificado=True).count()
                
                porcentaje = (presentes / total_reg * 100) if total_reg > 0 else 100
                total_asistencia_curso += porcentaje
                
                # Clasificar estudiante
                if porcentaje < 70:
                    estado = "Crítico"
                    estado_clase = "danger"
                    estudiantes_criticos += 1
                elif porcentaje < 85:
                    estado = "En Riesgo"
                    estado_clase = "warning"
                    estudiantes_riesgo += 1
                else:
                    estado = "Bueno"
                    estado_clase = "success"
                    estudiantes_buenos += 1
                
                estudiantes_detalle.append({
                    'id': estudiante.id,
                    'nombre': estudiante.usuario.get_full_name(),
                    'rut': estudiante.usuario.rut,
                    'total_clases': int(total_reg),
                    'presentes': int(presentes),
                    'ausentes': int(ausentes),
                    'justificados': int(justificados),
                    'porcentaje': float(round(porcentaje, 1)),
                    'estado': estado,
                    'estado_clase': estado_clase
                })
            
            # Ordenar por porcentaje de asistencia (menor a mayor)
            estudiantes_detalle.sort(key=lambda x: x['porcentaje'])
            
            # Promedio de asistencia del curso
            promedio_asistencia = total_asistencia_curso / len(estudiantes) if estudiantes else 0
            
            # Estadísticas por asignatura
            asignaturas_detalle = []
            asignaturas = Asignatura.objects.filter(
                asistencia__estudiante__curso=curso,
                asistencia__fecha_registro__date__gte=fecha_inicio,
                asistencia__fecha_registro__date__lte=fecha_fin
            ).distinct()
            
            for asignatura in asignaturas:
                asist_asignatura = Asistencia.objects.filter(
                    asignatura=asignatura,
                    estudiante__curso=curso,
                    fecha_registro__date__gte=fecha_inicio,
                    fecha_registro__date__lte=fecha_fin
                )
                
                total_asig = asist_asignatura.count()
                pres_asig = asist_asignatura.filter(presente=True).count()
                
                porcentaje_asig = (pres_asig / total_asig * 100) if total_asig > 0 else 100
                
                asignaturas_detalle.append({
                    'asignatura': asignatura.nombre,
                    'total_clases': int(total_asig),
                    'total_presentes': int(pres_asig),
                    'porcentaje': float(round(porcentaje_asig, 1))
                })
            
            # Ordenar por porcentaje
            asignaturas_detalle.sort(key=lambda x: x['porcentaje'])
            
            return JsonResponse({
                'success': True,
                'data': {
                    'curso': {
                        'id': curso.id,
                        'nombre': f"{curso.nivel}°{curso.letra}",
                        'total_estudiantes': len(estudiantes)
                    },
                    'estadisticas': {
                        'total_registros': sum(est['total_clases'] for est in estudiantes_detalle),
                        'promedio_asistencia': float(round(promedio_asistencia, 1)),
                        'estudiantes_criticos': int(estudiantes_criticos),
                        'estudiantes_riesgo': int(estudiantes_riesgo),
                        'estudiantes_buenos': int(estudiantes_buenos)
                    },
                    'estudiantes': estudiantes_detalle,
                    'asignaturas': asignaturas_detalle
                },
                'periodo': periodo,
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y')
            })
            
        except Exception as e:
            print(f"Error en reporte de asistencia de curso: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Error en reporte de asistencia de curso: {str(e)}'})

@method_decorator(login_required, name='dispatch')
class ListaEstudiantesViewSimple(View):
    """Vista para obtener la lista completa de estudiantes con sus datos"""
    
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            return JsonResponse({'error': 'No autorizado'}, status=403)
        
        try:
            estudiantes_data = []
            estudiantes = Estudiante.objects.all().order_by('curso__nivel', 'curso__letra', 'usuario__apellido_paterno', 'usuario__nombre')
            
            for estudiante in estudiantes:
                estudiantes_data.append({
                    'id': estudiante.id,
                    'nombre_completo': estudiante.usuario.get_full_name(),
                    'nombre': estudiante.usuario.nombre,
                    'apellido_paterno': estudiante.usuario.apellido_paterno,
                    'apellido_materno': estudiante.usuario.apellido_materno,
                    'rut': estudiante.usuario.rut,
                    'div': estudiante.usuario.div or '',
                    'rut_completo': f"{estudiante.usuario.rut}-{estudiante.usuario.div}" if estudiante.usuario.div else estudiante.usuario.rut,
                    'correo': estudiante.usuario.correo,
                    'curso': f"{estudiante.curso.nivel}°{estudiante.curso.letra}",
                    'curso_id': estudiante.curso.id
                })
            
            return JsonResponse({
                'success': True,
                'data': estudiantes_data,
                'total': len(estudiantes_data)
            })
            
        except Exception as e:
            print(f"Error en lista de estudiantes: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Error al obtener lista de estudiantes: {str(e)}'}) 