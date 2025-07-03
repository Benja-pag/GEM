from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from Core.models import Estudiante, Curso, Asistencia, AlumnoEvaluacion, AsignaturaImpartida, ProfesorJefe, Evaluacion, Clase
from Core.views.alumnos import get_horario_estudiante, get_asistencia_estudiante, get_evaluaciones_estudiante, get_promedio_estudiante
from .pdf_generators import generar_pdf_horario, generar_pdf_asistencia, generar_pdf_calificaciones, generar_pdf_asistencia_asignaturas_docente, generar_pdf_asistencia_curso_jefe, generar_pdf_evaluaciones_asignaturas_docente, generar_pdf_evaluaciones_curso_jefe, generar_pdf_analisis_ia
from django.db.models import Avg, Max, Min
from datetime import date, datetime
from Core.views.reportes_simple import get_periodo_fechas
from .pdf_generators import generar_pdf_reporte_estudiantes_riesgo
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@method_decorator(login_required, name='dispatch')
class DescargarHorarioPDFView(View):
    """
    Vista para descargar el horario del estudiante en PDF
    """
    def get(self, request):
        # Verificar que el usuario es un estudiante
        if not hasattr(request.user.usuario, 'estudiante'):
            return HttpResponse('No tienes permiso para acceder a esta página', status=403)
        
        estudiante = request.user.usuario.estudiante
        
        # Obtener datos del horario
        horario_data = get_horario_estudiante(request.user.id)
        
        # Generar PDF
        buffer = generar_pdf_horario(estudiante, horario_data)
        
        # Crear respuesta HTTP
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="horario_{estudiante.usuario.nombre}_{estudiante.usuario.apellido_paterno}.pdf"'
        
        return response

@method_decorator(login_required, name='dispatch')
class DescargarAsistenciaPDFView(View):
    """
    Vista para descargar el reporte de asistencia del estudiante en PDF
    """
    def get(self, request):
        # Verificar que el usuario es un estudiante
        if not hasattr(request.user.usuario, 'estudiante'):
            return HttpResponse('No tienes permiso para acceder a esta página', status=403)
        
        estudiante = request.user.usuario.estudiante
        
        # Obtener datos de asistencia
        asistencia_data = get_asistencia_estudiante(estudiante.pk)
        
        # Generar PDF
        buffer = generar_pdf_asistencia(estudiante, asistencia_data)
        
        # Crear respuesta HTTP
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="asistencia_{estudiante.usuario.nombre}_{estudiante.usuario.apellido_paterno}.pdf"'
        
        return response

@method_decorator(login_required, name='dispatch')
class DescargarCalificacionesPDFView(View):
    """
    Vista para descargar el reporte de calificaciones del estudiante en PDF
    """
    def get(self, request):
        # Verificar que el usuario es un estudiante
        if not hasattr(request.user.usuario, 'estudiante'):
            return HttpResponse('No tienes permiso para acceder a esta página', status=403)
        
        estudiante = request.user.usuario.estudiante
        
        # Obtener datos de calificaciones
        calificaciones_data = get_evaluaciones_estudiante(estudiante.pk)
        promedio = get_promedio_estudiante(estudiante.pk)
        
        # Generar PDF
        buffer = generar_pdf_calificaciones(estudiante, calificaciones_data, promedio)
        
        # Crear respuesta HTTP
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="calificaciones_{estudiante.usuario.nombre}_{estudiante.usuario.apellido_paterno}.pdf"'
        
        return response 

@method_decorator(login_required, name='dispatch')
class DescargarReporteCursosPDFView(View):
    """
    Vista para descargar el reporte de rendimiento por cursos en PDF
    """
    def get(self, request):
        # Verificar que el usuario es administrador
        if not request.user.is_authenticated or not request.user.is_admin:
            return HttpResponse('No tienes permiso para acceder a esta página', status=403)
        
        try:
            # Importar funciones necesarias
            from Core.views.reportes_simple import get_periodo_fechas
            from Core.views.pdf_generators import generar_pdf_reporte_cursos
            from Core.models import Curso, AlumnoEvaluacion, Asistencia
            from django.db.models import Avg
            from datetime import date
            
            # Obtener período (por defecto año actual)
            periodo = request.GET.get('periodo', 'ano_actual')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            # Obtener datos de cursos (misma lógica que la vista de reportes)
            cursos_data = []
            cursos = Curso.objects.all().order_by('nivel', 'letra')
            
            for curso in cursos:
                # Obtener estudiantes del curso
                estudiantes = curso.estudiantes.all()
                total_estudiantes = estudiantes.count()
                
                if total_estudiantes == 0:
                    # Curso sin estudiantes
                    cursos_data.append({
                        'curso': f"{curso.nivel}°{curso.letra}",
                        'total_estudiantes': 0,
                        'total_evaluaciones': 0,
                        'promedio_curso': 0.0,
                        'porcentaje_aprobacion': 0.0,
                        'porcentaje_asistencia': 0.0,
                        'estado': 'N/A'
                    })
                    continue
                
                # Calcular datos académicos
                promedios_estudiantes = []
                total_evaluaciones_curso = 0
                
                for estudiante in estudiantes:
                    # Obtener evaluaciones del estudiante
                    evaluaciones = AlumnoEvaluacion.objects.filter(
                        estudiante=estudiante,
                        evaluacion__fecha__gte=fecha_inicio,
                        evaluacion__fecha__lte=fecha_fin
                    )
                    
                    total_eval_estudiante = evaluaciones.count()
                    total_evaluaciones_curso += total_eval_estudiante
                    
                    if total_eval_estudiante > 0:
                        # Calcular promedio del estudiante
                        promedio_estudiante = evaluaciones.aggregate(promedio=Avg('nota'))['promedio']
                        promedios_estudiantes.append(promedio_estudiante)
                
                # Calcular promedio del curso
                estudiantes_con_notas = len(promedios_estudiantes)
                if estudiantes_con_notas > 0:
                    promedio_curso = sum(promedios_estudiantes) / estudiantes_con_notas
                    estudiantes_aprobados = len([p for p in promedios_estudiantes if p >= 4.0])
                    porcentaje_aprobacion = (estudiantes_aprobados / estudiantes_con_notas) * 100
                else:
                    promedio_curso = 0.0
                    porcentaje_aprobacion = 0.0
                
                # Calcular asistencia del curso
                asistencias = Asistencia.objects.filter(
                    estudiante__curso=curso,
                    fecha_registro__date__gte=fecha_inicio,
                    fecha_registro__date__lte=fecha_fin
                )
                total_asistencias = asistencias.count()
                presentes = asistencias.filter(presente=True).count()
                porcentaje_asistencia = (presentes / total_asistencias * 100) if total_asistencias > 0 else 0
                
                # Determinar estado basado en asistencia
                if porcentaje_asistencia < 83:
                    estado = "Crítico"
                elif porcentaje_asistencia < 85:
                    estado = "Regular"
                else:
                    estado = "Bueno"
                
                cursos_data.append({
                    'curso': f"{curso.nivel}°{curso.letra}",
                    'total_estudiantes': total_estudiantes,
                    'total_evaluaciones': total_evaluaciones_curso,
                    'promedio_curso': promedio_curso,
                    'porcentaje_aprobacion': porcentaje_aprobacion,
                    'porcentaje_asistencia': porcentaje_asistencia,
                    'estado': estado
                })
            
            # Información del período
            periodo_info = {
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                'periodo': periodo
            }
            
            # Generar PDF
            buffer = generar_pdf_reporte_cursos(cursos_data, periodo_info)
            
            # Crear respuesta HTTP
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            filename = f"reporte_cursos_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            return HttpResponse(f'Error al generar el reporte: {str(e)}', status=500)

@method_decorator(login_required, name='dispatch')
class DescargarReporteAsistenciaPDFView(View):
    """
    Vista para descargar el reporte de asistencia por cursos en PDF
    """
    def get(self, request):
        # Verificar que el usuario es administrador
        if not request.user.is_authenticated or not request.user.is_admin:
            return HttpResponse('No tienes permiso para acceder a esta página', status=403)
        
        try:
            # Importar funciones necesarias
            from Core.views.reportes_simple import get_periodo_fechas
            from Core.views.pdf_generators import generar_pdf_reporte_asistencia
            from Core.models import Curso, Asistencia
            from datetime import date
            
            # Obtener período (por defecto año actual)
            periodo = request.GET.get('periodo', 'ano_actual')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            # Obtener datos de asistencia por cursos (misma lógica que la vista de reportes)
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
                        'estado': 'N/A'
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
                elif porcentaje_asistencia < 85:
                    estado = "Regular"
                else:
                    estado = "Bueno"
                
                cursos_asistencia.append({
                    'curso': f"{curso.nivel}°{curso.letra}",
                    'total_estudiantes': total_estudiantes,
                    'total_registros': total_registros,
                    'presentes': presentes,
                    'ausentes': ausentes,
                    'justificados': justificados,
                    'porcentaje_asistencia': porcentaje_asistencia,
                    'estudiantes_riesgo': estudiantes_riesgo,
                    'estado': estado
                })
            
            # Información del período
            periodo_info = {
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                'periodo': periodo
            }
            
            # Generar PDF
            buffer = generar_pdf_reporte_asistencia(cursos_asistencia, periodo_info)
            
            # Crear respuesta HTTP
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            filename = f"reporte_asistencia_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            return HttpResponse(f'Error al generar el reporte: {str(e)}', status=500)

@method_decorator(login_required, name='dispatch')
class DescargarReporteEstudiantesRiesgoPDFView(View):
    """Vista para descargar el PDF del reporte de estudiantes en riesgo"""
    
    def get(self, request):
        # Verificar permisos de administrador
        if not request.user.is_authenticated or not request.user.is_admin:
            return HttpResponseForbidden("No tienes permisos para acceder a este reporte")
        
        try:
            # Obtener parámetros
            periodo = request.GET.get('periodo', 'ano_actual')
            tipo_reporte = request.GET.get('tipo', 'completo')  # completo, academico, asistencia
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
                    # Si hay error con un estudiante específico, continuar
                    continue
            
            # Ordenar por promedio/asistencia
            estudiantes_riesgo_notas.sort(key=lambda x: x['promedio'])
            estudiantes_riesgo_asistencia.sort(key=lambda x: x['asistencia'])
            
            # Filtrar datos según el tipo de reporte
            if tipo_reporte == 'academico':
                data_riesgo = {
                    'riesgo_notas': estudiantes_riesgo_notas,
                    'riesgo_asistencia': []
                }
                nombre_archivo = f'reporte_riesgo_academico_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
                titulo_reporte = "REPORTE DE RIESGO ACADÉMICO"
            elif tipo_reporte == 'asistencia':
                data_riesgo = {
                    'riesgo_notas': [],
                    'riesgo_asistencia': estudiantes_riesgo_asistencia
                }
                nombre_archivo = f'reporte_riesgo_asistencia_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
                titulo_reporte = "REPORTE DE RIESGO DE ASISTENCIA"
            else:  # completo
                data_riesgo = {
                    'riesgo_notas': estudiantes_riesgo_notas,
                    'riesgo_asistencia': estudiantes_riesgo_asistencia
                }
                nombre_archivo = f'reporte_estudiantes_riesgo_completo_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
                titulo_reporte = "REPORTE COMPLETO DE ESTUDIANTES EN RIESGO"
            
            periodo_info = {
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                'tipo_reporte': tipo_reporte,
                'titulo_reporte': titulo_reporte
            }
            
            # Generar PDF
            pdf_buffer = generar_pdf_reporte_estudiantes_riesgo(data_riesgo, periodo_info)
            
            # Crear respuesta HTTP con el PDF
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            
            return response
            
        except Exception as e:
            return HttpResponse(f"Error al generar el PDF: {str(e)}", status=500)

@method_decorator(login_required, name='dispatch')
class DescargarAsistenciaEstudiantePDFView(View):
    """Vista para descargar el PDF del reporte de asistencia de un estudiante específico"""
    
    def get(self, request):
        # Verificar permisos de administrador
        if not request.user.is_authenticated or not request.user.is_admin:
            return HttpResponseForbidden("No tienes permisos para acceder a este reporte")
        
        try:
            # Obtener parámetros
            estudiante_id = request.GET.get('estudiante_id')
            if not estudiante_id:
                return HttpResponse("ID de estudiante requerido", status=400)
            
            periodo = request.GET.get('periodo', 'ano_actual')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            try:
                estudiante = Estudiante.objects.get(id=estudiante_id)
            except Estudiante.DoesNotExist:
                return HttpResponse("Estudiante no encontrado", status=404)
            
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
            elif porcentaje_asistencia < 85:
                estado = "En Riesgo"
            else:
                estado = "Bueno"
            
            # Detalle por asignatura
            asignaturas_detalle = []
            asignaturas = set(asistencias.values_list('clase__asignatura_impartida__asignatura__nombre', flat=True))
            
            for asignatura_nombre in asignaturas:
                asist_asignatura = asistencias.filter(clase__asignatura_impartida__asignatura__nombre=asignatura_nombre)
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
                    'asignatura': asistencia.clase.asignatura_impartida.asignatura.nombre,
                    'presente': asistencia.presente,
                    'justificado': asistencia.justificado if not asistencia.presente else None,
                    'observaciones': asistencia.observaciones or ''
                })
            
            # Preparar datos para el PDF
            estudiante_data = {
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
                    'estado': estado
                },
                'asignaturas': asignaturas_detalle,
                'historial': historial_reciente
            }
            
            periodo_info = {
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                'periodo': periodo
            }
            
            # Generar PDF
            from Core.views.pdf_generators import generar_pdf_asistencia_estudiante
            pdf_buffer = generar_pdf_asistencia_estudiante(estudiante_data, periodo_info)
            
            # Crear respuesta HTTP con el PDF
            nombre_archivo = f'asistencia_{estudiante.usuario.rut}_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            
            return response
            
        except Exception as e:
            return HttpResponse(f"Error al generar el PDF: {str(e)}", status=500)

@method_decorator(login_required, name='dispatch')
class DescargarAsistenciaCursoPDFView(View):
    """Vista para descargar el PDF del reporte de asistencia de un curso específico"""
    
    def get(self, request):
        # Verificar permisos de administrador
        if not request.user.is_authenticated or not request.user.is_admin:
            return HttpResponseForbidden("No tienes permisos para acceder a este reporte")
        
        try:
            # Obtener parámetros
            curso_id = request.GET.get('curso_id')
            if not curso_id:
                return HttpResponse("ID de curso requerido", status=400)
            
            periodo = request.GET.get('periodo', 'ano_actual')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            try:
                curso = Curso.objects.get(id=curso_id)
            except Curso.DoesNotExist:
                return HttpResponse("Curso no encontrado", status=404)
            
            # Obtener estudiantes del curso
            estudiantes = curso.estudiantes.all().order_by('usuario__apellido_paterno', 'usuario__nombre')
            
            if not estudiantes.exists():
                # Curso sin estudiantes
                curso_data = {
                    'curso': {
                        'id': curso.id,
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
                }
            else:
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
                        estudiantes_criticos += 1
                    elif porcentaje < 85:
                        estado = "En Riesgo"
                        estudiantes_riesgo += 1
                    else:
                        estado = "Bueno"
                        estudiantes_buenos += 1
                    
                    estudiantes_detalle.append({
                        'id': estudiante.pk,
                        'nombre': estudiante.usuario.get_full_name(),
                        'rut': estudiante.usuario.rut,
                        'total_clases': int(total_reg),
                        'presentes': int(presentes),
                        'ausentes': int(ausentes),
                        'justificados': int(justificados),
                        'porcentaje': float(round(porcentaje, 1)),
                        'estado': estado
                    })
                
                # Ordenar por porcentaje de asistencia (menor a mayor)
                estudiantes_detalle.sort(key=lambda x: x['porcentaje'])
                
                # Promedio de asistencia del curso
                promedio_asistencia = total_asistencia_curso / len(estudiantes) if estudiantes else 0
                
                # Estadísticas por asignatura
                asignaturas_detalle = []
                from Core.models import Asignatura
                # Obtener asignaturas que tienen clases con asistencia registrada para este curso
                asignaturas = Asignatura.objects.filter(
                    imparticiones__clases__asistencias__estudiante__curso=curso,
                    imparticiones__clases__asistencias__fecha_registro__date__gte=fecha_inicio,
                    imparticiones__clases__asistencias__fecha_registro__date__lte=fecha_fin
                ).distinct()
                
                for asignatura in asignaturas:
                    # Obtener asistencias de esta asignatura para el curso específico
                    asist_asignatura = Asistencia.objects.filter(
                        clase__asignatura_impartida__asignatura=asignatura,
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
                
                curso_data = {
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
                 }
            
            periodo_info = {
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                'periodo': periodo
            }
            
            # Generar PDF
            from Core.views.pdf_generators import generar_pdf_asistencia_curso
            pdf_buffer = generar_pdf_asistencia_curso(curso_data, periodo_info)
            
            # Crear respuesta HTTP con el PDF
            nombre_archivo = f'asistencia_curso_{curso.nivel}{curso.letra}_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            
            return response
            
        except Exception as e:
            return HttpResponse(f"Error al generar el PDF: {str(e)}", status=500)

@method_decorator(login_required, name='dispatch')
class DescargarAsistenciaEstudianteAdminPDFView(View):
    """Vista para que el admin descargue PDF de asistencia de cualquier estudiante usando la misma lógica del panel de estudiante"""
    
    def get(self, request):
        # Verificar permisos de administrador
        try:
            from Core.models import Administrativo
            admin_user = Administrativo.objects.filter(
                usuario__auth_user=request.user,
                rol='ADMINISTRADOR'
            ).first()
            
            if not admin_user:
                return HttpResponseForbidden("No tienes permisos para acceder a este reporte")
        except:
            return HttpResponseForbidden("No tienes permisos para acceder a este reporte")
        
        try:
            # Obtener parámetros
            estudiante_id = request.GET.get('estudiante_id')
            if not estudiante_id:
                return HttpResponse("ID de estudiante requerido", status=400)
            
            try:
                estudiante = Estudiante.objects.get(pk=estudiante_id)
            except Estudiante.DoesNotExist:
                return HttpResponse("Estudiante no encontrado", status=404)
            
            # Usar la misma función que el panel de estudiante
            from Core.views.alumnos import get_asistencia_estudiante
            from Core.views.pdf_generators import generar_pdf_asistencia
            
            # Obtener datos de asistencia usando la función del panel de estudiante
            asistencia_data = get_asistencia_estudiante(estudiante.pk)
            
            # Generar PDF usando el mismo generador del panel de estudiante
            buffer = generar_pdf_asistencia(estudiante, asistencia_data)
            
            # Crear respuesta HTTP con el PDF
            nombre_archivo = f'asistencia_{estudiante.usuario.nombre}_{estudiante.usuario.apellido_paterno}.pdf'
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            
            return response
            
        except Exception as e:
            return HttpResponse(f"Error al generar el PDF: {str(e)}", status=500)

@method_decorator(login_required, name='dispatch')
class DescargarPromedioAsignaturasCursoPDFView(View):
    """Vista para descargar PDF de promedios por asignatura de un curso específico"""
    
    def get(self, request):
        # Verificar permisos de administrador
        try:
            from Core.models import Administrativo
            admin_user = Administrativo.objects.filter(
                usuario__auth_user=request.user,
                rol='ADMINISTRADOR'
            ).first()
            
            if not admin_user:
                return HttpResponseForbidden("No tienes permisos para acceder a este reporte")
        except:
            return HttpResponseForbidden("No tienes permisos para acceder a este reporte")
        
        try:
            # Obtener parámetros
            curso_id = request.GET.get('curso_id')
            if not curso_id:
                return HttpResponse("ID de curso requerido", status=400)
            
            try:
                curso = Curso.objects.get(pk=curso_id)
            except Curso.DoesNotExist:
                return HttpResponse("Curso no encontrado", status=404)
            
            # Obtener datos de promedios por asignatura del curso
            from Core.views.reportes_simple import get_periodo_fechas
            from Core.models import AsignaturaImpartida, AlumnoEvaluacion, Asignatura
            from django.db.models import Avg, Count
            
            periodo = request.GET.get('periodo', 'ano_actual')
            fecha_inicio, fecha_fin = get_periodo_fechas(periodo)
            
            # Obtener asignaturas impartidas al curso
            asignaturas_impartidas = AsignaturaImpartida.objects.filter(
                inscripciones__estudiante__curso=curso,
                inscripciones__validada=True
            ).select_related('asignatura', 'docente__usuario').distinct()
            
            asignaturas_data = []
            
            for asignatura_impartida in asignaturas_impartidas:
                asignatura = asignatura_impartida.asignatura
                docente = asignatura_impartida.docente
                
                # Obtener evaluaciones de esta asignatura para estudiantes del curso
                evaluaciones = AlumnoEvaluacion.objects.filter(
                    estudiante__curso=curso,
                    evaluacion__clase__asignatura_impartida=asignatura_impartida,
                    evaluacion__fecha__gte=fecha_inicio,
                    evaluacion__fecha__lte=fecha_fin
                )
                
                if evaluaciones.exists():
                    # Calcular estadísticas
                    total_notas = evaluaciones.count()
                    promedio = evaluaciones.aggregate(promedio=Avg('nota'))['promedio']
                    aprobados = evaluaciones.filter(nota__gte=4.0).count()
                    porcentaje_aprobacion = (aprobados / total_notas * 100) if total_notas > 0 else 0
                    
                    # Obtener número de estudiantes únicos
                    estudiantes_evaluados = evaluaciones.values('estudiante').distinct().count()
                    
                    # Determinar estado
                    if promedio >= 5.5:
                        estado = "Excelente"
                    elif promedio >= 4.5:
                        estado = "Bueno"
                    elif promedio >= 4.0:
                        estado = "Regular"
                    else:
                        estado = "Deficiente"
                    
                    asignaturas_data.append({
                        'asignatura': asignatura.nombre,
                        'docente': docente.usuario.get_full_name(),
                        'total_evaluaciones': total_notas,
                        'estudiantes_evaluados': estudiantes_evaluados,
                        'promedio': float(round(promedio, 2)),
                        'aprobados': aprobados,
                        'porcentaje_aprobacion': float(round(porcentaje_aprobacion, 1)),
                        'estado': estado
                    })
            
            # Ordenar por promedio descendente
            asignaturas_data.sort(key=lambda x: x['promedio'], reverse=True)
            
            # Preparar datos para el PDF
            curso_data = {
                'curso': {
                    'id': curso.id,
                    'nombre': f"{curso.nivel}°{curso.letra}",
                    'total_estudiantes': curso.estudiantes.count(),
                    'total_asignaturas': len(asignaturas_data)
                },
                'estadisticas': {
                    'total_evaluaciones': sum(asig['total_evaluaciones'] for asig in asignaturas_data),
                    'promedio_general': sum(asig['promedio'] for asig in asignaturas_data) / len(asignaturas_data) if asignaturas_data else 0,
                    'asignaturas_excelentes': len([a for a in asignaturas_data if a['estado'] == 'Excelente']),
                    'asignaturas_buenas': len([a for a in asignaturas_data if a['estado'] == 'Bueno']),
                    'asignaturas_regulares': len([a for a in asignaturas_data if a['estado'] == 'Regular']),
                    'asignaturas_deficientes': len([a for a in asignaturas_data if a['estado'] == 'Deficiente'])
                },
                'asignaturas': asignaturas_data
            }
            
            periodo_info = {
                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                'periodo': periodo
            }
            
            # Generar PDF
            from Core.views.pdf_generators import generar_pdf_promedio_asignaturas_curso
            pdf_buffer = generar_pdf_promedio_asignaturas_curso(curso_data, periodo_info)
            
            # Crear respuesta HTTP con el PDF
            nombre_archivo = f'promedios_asignaturas_{curso.nivel}{curso.letra}_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            
            return response
            
        except Exception as e:
            return HttpResponse(f"Error al generar el PDF: {str(e)}", status=500)

@method_decorator(login_required, name='dispatch')
class DescargarAsistenciaAsignaturasCursoPDFView(View):
    """
    Vista para descargar el reporte de asistencia por asignaturas de un curso en PDF
    """
    def get(self, request):
        # Verificar permisos de administrador
        if not request.user.is_authenticated or not request.user.is_admin:
            return HttpResponse('No tienes permiso para acceder a esta página', status=403)
        
        try:
            curso_id = request.GET.get('curso_id')
            if not curso_id:
                return HttpResponse('ID de curso requerido', status=400)
            
            # Obtener el curso
            try:
                curso = Curso.objects.get(id=curso_id)
            except Curso.DoesNotExist:
                return HttpResponse('Curso no encontrado', status=404)
            
            # Importar funciones necesarias
            from Core.models import AsignaturaImpartida, Asistencia
            from Core.views.pdf_generators import generar_pdf_asistencia_asignaturas_curso
            
            # Obtener todas las asignaturas impartidas en el curso
            asignaturas_curso = AsignaturaImpartida.objects.filter(
                clases__curso=curso
            ).distinct().select_related('asignatura', 'docente__usuario')
            
            asignaturas_data = []
            
            for asignatura_impartida in asignaturas_curso:
                # Obtener todas las clases de esta asignatura en el curso
                clases_asignatura = asignatura_impartida.clases.filter(curso=curso)
                
                # Calcular asistencia para esta asignatura
                total_registros = 0
                total_presentes = 0
                estudiantes_evaluados = set()
                
                # Obtener estudiantes del curso
                estudiantes_curso = curso.estudiantes.all()
                
                for estudiante in estudiantes_curso:
                    # Buscar registros de asistencia para las clases de esta asignatura
                    asistencias_estudiante = Asistencia.objects.filter(
                        estudiante=estudiante,
                        clase__in=clases_asignatura
                    )
                    
                    if asistencias_estudiante.exists():
                        estudiantes_evaluados.add(estudiante.pk)
                        total_registros += asistencias_estudiante.count()
                        total_presentes += asistencias_estudiante.filter(presente=True).count()
                
                # Calcular porcentaje de asistencia
                porcentaje_asistencia = 0
                if total_registros > 0:
                    porcentaje_asistencia = round((total_presentes * 100) / total_registros, 1)
                
                # Determinar estado basado en asistencia
                if porcentaje_asistencia >= 85:
                    estado = "Excelente"
                elif porcentaje_asistencia >= 75:
                    estado = "Bueno"
                elif porcentaje_asistencia >= 60:
                    estado = "Regular"
                else:
                    estado = "Deficiente"
                
                # Información del docente
                docente_nombre = "Sin asignar"
                if asignatura_impartida.docente:
                    docente_nombre = asignatura_impartida.docente.usuario.get_full_name()
                
                asignaturas_data.append({
                    'asignatura': asignatura_impartida.asignatura.nombre,
                    'docente': docente_nombre,
                    'total_clases': clases_asignatura.count(),
                    'estudiantes_evaluados': len(estudiantes_evaluados),
                    'total_registros': total_registros,
                    'total_presentes': total_presentes,
                    'total_ausentes': total_registros - total_presentes,
                    'porcentaje_asistencia': porcentaje_asistencia,
                    'estado': estado
                })
            
            # Ordenar por porcentaje de asistencia descendente
            asignaturas_data.sort(key=lambda x: x['porcentaje_asistencia'], reverse=True)
            
            # Calcular estadísticas generales del curso
            if asignaturas_data:
                promedio_asistencia_curso = sum(a['porcentaje_asistencia'] for a in asignaturas_data) / len(asignaturas_data)
                total_estudiantes_curso = curso.estudiantes.count()
                total_asignaturas = len(asignaturas_data)
            else:
                promedio_asistencia_curso = 0
                total_estudiantes_curso = curso.estudiantes.count()
                total_asignaturas = 0
            
            # Datos del curso
            curso_data = {
                'curso': f"{curso.nivel}°{curso.letra}",
                'total_estudiantes': total_estudiantes_curso,
                'total_asignaturas': total_asignaturas,
                'promedio_asistencia_curso': round(promedio_asistencia_curso, 1),
                'asignaturas': asignaturas_data
            }
            
            # Generar PDF
            buffer = generar_pdf_asistencia_asignaturas_curso(curso_data)
            
            # Crear respuesta HTTP
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="asistencia_asignaturas_{curso.nivel}{curso.letra}_{date.today().strftime("%Y%m%d")}.pdf"'
            
            return response
            
        except Exception as e:
            print(f"Error generando PDF de asistencia por asignaturas: {str(e)}")
            return HttpResponse(f'Error generando PDF: {str(e)}', status=500)

@method_decorator(login_required, name='dispatch')
class DescargarEvaluacionesAsignaturasCursoPDFView(View):
    """
    Vista para descargar el reporte de evaluaciones por asignaturas de un curso en PDF
    """
    def get(self, request):
        # Verificar permisos de administrador
        if not request.user.is_authenticated or not request.user.is_admin:
            return HttpResponse('No tienes permiso para acceder a esta página', status=403)
        
        try:
            curso_id = request.GET.get('curso_id')
            if not curso_id:
                return HttpResponse('ID de curso requerido', status=400)
            
            # Obtener el curso
            try:
                curso = Curso.objects.get(id=curso_id)
            except Curso.DoesNotExist:
                return HttpResponse('Curso no encontrado', status=404)
            
            # Importar funciones necesarias
            from Core.models import AsignaturaImpartida, Evaluacion, AlumnoEvaluacion
            from Core.views.pdf_generators import generar_pdf_evaluaciones_asignaturas_curso
            from django.db.models import Avg
            
            # Obtener todas las asignaturas impartidas en el curso
            asignaturas_curso = AsignaturaImpartida.objects.filter(
                clases__curso=curso
            ).distinct().select_related('asignatura', 'docente__usuario')
            
            asignaturas_data = []
            
            for asignatura_impartida in asignaturas_curso:
                # Obtener todas las evaluaciones de esta asignatura en el curso
                evaluaciones_asignatura = Evaluacion.objects.filter(
                    clase__asignatura_impartida=asignatura_impartida,
                    clase__curso=curso
                )
                
                # Calcular estadísticas de evaluaciones
                total_evaluaciones = evaluaciones_asignatura.count()
                
                if total_evaluaciones > 0:
                    # Obtener todas las notas de los estudiantes del curso para esta asignatura
                    notas_curso = AlumnoEvaluacion.objects.filter(
                        evaluacion__in=evaluaciones_asignatura,
                        estudiante__curso=curso
                    )
                    
                    total_notas = notas_curso.count()
                    estudiantes_evaluados = notas_curso.values('estudiante').distinct().count()
                    
                    if total_notas > 0:
                        promedio_asignatura = notas_curso.aggregate(promedio=Avg('nota'))['promedio']
                        aprobados = notas_curso.filter(nota__gte=4.0).count()
                        reprobados = notas_curso.filter(nota__lt=4.0).count()
                        porcentaje_aprobacion = (aprobados / total_notas * 100)
                        
                        # Determinar estado basado en promedio
                        if promedio_asignatura >= 5.5:
                            estado = "Excelente"
                        elif promedio_asignatura >= 4.5:
                            estado = "Bueno"
                        elif promedio_asignatura >= 4.0:
                            estado = "Regular"
                        else:
                            estado = "Deficiente"
                    else:
                        promedio_asignatura = 0
                        aprobados = 0
                        reprobados = 0
                        porcentaje_aprobacion = 0
                        estado = "Sin datos"
                else:
                    total_notas = 0
                    estudiantes_evaluados = 0
                    promedio_asignatura = 0
                    aprobados = 0
                    reprobados = 0
                    porcentaje_aprobacion = 0
                    estado = "Sin evaluaciones"
                
                # Información del docente
                docente_nombre = "Sin asignar"
                if asignatura_impartida.docente:
                    docente_nombre = asignatura_impartida.docente.usuario.get_full_name()
                
                asignaturas_data.append({
                    'asignatura': asignatura_impartida.asignatura.nombre,
                    'docente': docente_nombre,
                    'total_evaluaciones': total_evaluaciones,
                    'estudiantes_evaluados': estudiantes_evaluados,
                    'total_notas': total_notas,
                    'promedio_asignatura': round(promedio_asignatura, 2) if promedio_asignatura else 0,
                    'aprobados': aprobados,
                    'reprobados': reprobados,
                    'porcentaje_aprobacion': round(porcentaje_aprobacion, 1) if porcentaje_aprobacion else 0,
                    'estado': estado
                })
            
            # Ordenar por promedio descendente
            asignaturas_data.sort(key=lambda x: x['promedio_asignatura'], reverse=True)
            
            # Calcular estadísticas generales del curso
            if asignaturas_data:
                # Filtrar asignaturas con datos
                asignaturas_con_datos = [a for a in asignaturas_data if a['total_notas'] > 0]
                
                if asignaturas_con_datos:
                    promedio_general_curso = sum(a['promedio_asignatura'] for a in asignaturas_con_datos) / len(asignaturas_con_datos)
                    total_evaluaciones_curso = sum(a['total_evaluaciones'] for a in asignaturas_data)
                    total_notas_curso = sum(a['total_notas'] for a in asignaturas_data)
                    total_aprobados = sum(a['aprobados'] for a in asignaturas_data)
                    porcentaje_aprobacion_curso = (total_aprobados / total_notas_curso * 100) if total_notas_curso > 0 else 0
                else:
                    promedio_general_curso = 0
                    total_evaluaciones_curso = 0
                    total_notas_curso = 0
                    porcentaje_aprobacion_curso = 0
                
                total_estudiantes_curso = curso.estudiantes.count()
                total_asignaturas = len(asignaturas_data)
            else:
                promedio_general_curso = 0
                total_evaluaciones_curso = 0
                total_notas_curso = 0
                porcentaje_aprobacion_curso = 0
                total_estudiantes_curso = curso.estudiantes.count()
                total_asignaturas = 0
            
            # Datos del curso
            curso_data = {
                'curso': f"{curso.nivel}°{curso.letra}",
                'total_estudiantes': total_estudiantes_curso,
                'total_asignaturas': total_asignaturas,
                'total_evaluaciones': total_evaluaciones_curso,
                'total_notas': total_notas_curso,
                'promedio_general_curso': round(promedio_general_curso, 2),
                'porcentaje_aprobacion_curso': round(porcentaje_aprobacion_curso, 1),
                'asignaturas': asignaturas_data
            }
            
            # Generar PDF
            buffer = generar_pdf_evaluaciones_asignaturas_curso(curso_data)
            
            # Crear respuesta HTTP
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="evaluaciones_asignaturas_{curso.nivel}{curso.letra}_{date.today().strftime("%Y%m%d")}.pdf"'
            
            return response
            
        except Exception as e:
            print(f"Error generando PDF de evaluaciones por asignaturas: {str(e)}")
            return HttpResponse(f'Error generando PDF: {str(e)}', status=500)

@method_decorator(login_required, name='dispatch')
class DescargarEvaluacionesEstudianteAdminPDFView(View):
    """Vista para que el admin descargue PDF de evaluaciones de cualquier estudiante"""
    
    def get(self, request):
        # Verificar permisos de administrador
        try:
            from Core.models import Administrativo
            admin_user = Administrativo.objects.filter(
                usuario__auth_user=request.user,
                rol='ADMINISTRADOR'
            ).first()
            
            if not admin_user:
                return HttpResponseForbidden("No tienes permisos para acceder a este reporte")
        except:
            return HttpResponseForbidden("No tienes permisos para acceder a este reporte")
        
        try:
            # Obtener parámetros
            estudiante_id = request.GET.get('estudiante_id')
            if not estudiante_id:
                return HttpResponse("ID de estudiante requerido", status=400)
            
            try:
                estudiante = Estudiante.objects.get(pk=estudiante_id)
            except Estudiante.DoesNotExist:
                return HttpResponse("Estudiante no encontrado", status=404)
            
            # Obtener datos de evaluaciones del estudiante
            from Core.models import AlumnoEvaluacion, AsignaturaImpartida, AsignaturaInscrita
            from django.db.models import Avg, Count, Max, Min
            
            # Obtener asignaturas en las que está inscrito el estudiante
            inscripciones = AsignaturaInscrita.objects.filter(
                estudiante=estudiante,
                validada=True
            ).select_related('asignatura_impartida__asignatura', 'asignatura_impartida__docente__usuario')
            
            asignaturas_data = []
            total_evaluaciones_estudiante = 0
            total_notas_estudiante = 0
            suma_notas = 0
            
            for inscripcion in inscripciones:
                asignatura_impartida = inscripcion.asignatura_impartida
                
                # Obtener todas las evaluaciones del estudiante para esta asignatura
                evaluaciones_estudiante = AlumnoEvaluacion.objects.filter(
                    estudiante=estudiante,
                    evaluacion__clase__asignatura_impartida=asignatura_impartida
                ).select_related('evaluacion')
                
                if evaluaciones_estudiante.exists():
                    # Calcular estadísticas
                    total_evaluaciones = evaluaciones_estudiante.count()
                    promedio = evaluaciones_estudiante.aggregate(promedio=Avg('nota'))['promedio']
                    nota_maxima = evaluaciones_estudiante.aggregate(max_nota=Max('nota'))['max_nota']
                    nota_minima = evaluaciones_estudiante.aggregate(min_nota=Min('nota'))['min_nota']
                    aprobadas = evaluaciones_estudiante.filter(nota__gte=4.0).count()
                    reprobadas = evaluaciones_estudiante.filter(nota__lt=4.0).count()
                    
                    # Determinar estado
                    if promedio >= 5.5:
                        estado = "Excelente"
                    elif promedio >= 4.5:
                        estado = "Bueno"
                    elif promedio >= 4.0:
                        estado = "Regular"
                    else:
                        estado = "Deficiente"
                    
                    # Obtener detalle de evaluaciones
                    evaluaciones_detalle = []
                    for eval_alumno in evaluaciones_estudiante.order_by('-evaluacion__fecha'):
                        evaluaciones_detalle.append({
                            'fecha': eval_alumno.evaluacion.fecha.strftime('%d/%m/%Y'),
                            'tipo': eval_alumno.evaluacion.evaluacion_base.nombre,
                            'descripcion': eval_alumno.evaluacion.evaluacion_base.descripcion or eval_alumno.evaluacion.observaciones or '',
                            'nota': float(eval_alumno.nota),
                            'estado': 'Aprobada' if eval_alumno.nota >= 4.0 else 'Reprobada'
                        })
                    
                    asignaturas_data.append({
                        'asignatura': asignatura_impartida.asignatura.nombre,
                        'docente': asignatura_impartida.docente.usuario.get_full_name(),
                        'total_evaluaciones': total_evaluaciones,
                        'promedio': float(round(promedio, 2)),
                        'nota_maxima': float(nota_maxima),
                        'nota_minima': float(nota_minima),
                        'aprobadas': aprobadas,
                        'reprobados': reprobadas,
                        'estado': estado,
                        'evaluaciones_detalle': evaluaciones_detalle
                    })
                    
                    total_evaluaciones_estudiante += total_evaluaciones
                    total_notas_estudiante += total_evaluaciones
                    suma_notas += promedio * total_evaluaciones
            
            # Calcular estadísticas generales del estudiante
            promedio_general = suma_notas / total_notas_estudiante if total_notas_estudiante > 0 else 0
            
            # Obtener mejor y peor nota
            todas_evaluaciones = AlumnoEvaluacion.objects.filter(
                estudiante=estudiante
            )
            
            mejor_nota = 0
            peor_nota = 0
            total_aprobadas = 0
            
            if todas_evaluaciones.exists():
                mejor_nota = todas_evaluaciones.aggregate(max_nota=Max('nota'))['max_nota']
                peor_nota = todas_evaluaciones.aggregate(min_nota=Min('nota'))['min_nota']
                total_aprobadas = todas_evaluaciones.filter(nota__gte=4.0).count()
            
            porcentaje_aprobacion = (total_aprobadas / total_evaluaciones_estudiante * 100) if total_evaluaciones_estudiante > 0 else 0
            
            # Ordenar asignaturas por promedio descendente
            asignaturas_data.sort(key=lambda x: x['promedio'], reverse=True)
            
            # Preparar datos para el PDF
            estudiante_data = {
                'estudiante': {
                    'nombre': estudiante.usuario.get_full_name(),
                    'rut': estudiante.usuario.rut,
                    'email': estudiante.usuario.correo,
                    'curso': f"{estudiante.curso.nivel}°{estudiante.curso.letra}" if estudiante.curso else "Sin curso"
                },
                'estadisticas': {
                    'total_asignaturas': len(asignaturas_data),
                    'total_evaluaciones': total_evaluaciones_estudiante,
                    'promedio_general': round(promedio_general, 2),
                    'mejor_nota': float(mejor_nota) if mejor_nota else 0,
                    'peor_nota': float(peor_nota) if peor_nota else 0,
                    'porcentaje_aprobacion': round(porcentaje_aprobacion, 1)
                },
                'asignaturas': asignaturas_data
            }
            
            # Generar PDF
            from Core.views.pdf_generators import generar_pdf_evaluaciones_estudiante
            buffer = generar_pdf_evaluaciones_estudiante(estudiante_data)
            
            # Crear respuesta HTTP con el PDF
            nombre_archivo = f'evaluaciones_{estudiante.usuario.nombre}_{estudiante.usuario.apellido_paterno}_{date.today().strftime("%Y%m%d")}.pdf'
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            
            return response
            
        except Exception as e:
            print(f"Error generando PDF de evaluaciones del estudiante: {str(e)}")
            return HttpResponse(f"Error al generar el PDF: {str(e)}", status=500)

@method_decorator(login_required, name='dispatch')
class DescargarReporteEvaluacionesGeneralPDFView(View):
    """Vista para descargar PDF del reporte general de evaluaciones de todos los cursos"""
    
    def get(self, request):
        # Verificar permisos de administrador
        try:
            from Core.models import Administrativo
            admin_user = Administrativo.objects.filter(
                usuario__auth_user=request.user,
                rol='ADMINISTRADOR'
            ).first()
            
            if not admin_user:
                return HttpResponseForbidden("No tienes permisos para acceder a este reporte")
        except:
            return HttpResponseForbidden("No tienes permisos para acceder a este reporte")
        
        try:
            # Obtener datos del reporte general usando la misma vista API
            from Core.views.reportes_simple import ReporteEvaluacionesGeneralViewSimple
            
            # Crear una instancia de la vista para obtener los datos
            vista_api = ReporteEvaluacionesGeneralViewSimple()
            vista_api.request = request
            
            # Obtener los datos usando el método get de la vista
            try:
                response = vista_api.get(request)
                if hasattr(response, 'content'):
                    import json
                    response_data = json.loads(response.content.decode('utf-8'))
                    if response_data.get('success'):
                        data = response_data.get('data')
                        if not data:
                            return HttpResponse("No hay datos disponibles para generar el reporte", status=404)
                    else:
                        return HttpResponse(f"Error en API: {response_data.get('error', 'Error desconocido')}", status=500)
                else:
                    return HttpResponse("Error al obtener respuesta de la API", status=500)
            except Exception as e:
                return HttpResponse(f"Error al obtener datos: {str(e)}", status=500)
            
            # Generar PDF
            from Core.views.pdf_generators import generar_pdf_reporte_evaluaciones_general
            buffer = generar_pdf_reporte_evaluaciones_general(data)
            
            # Crear respuesta HTTP con el PDF
            nombre_archivo = f'reporte_evaluaciones_general_{date.today().strftime("%Y%m%d")}.pdf'
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            
            return response
            
        except Exception as e:
            print(f"Error generando PDF del reporte general: {str(e)}")
            return HttpResponse(f"Error al generar el PDF: {str(e)}", status=500)

@method_decorator(login_required, name='dispatch')
class DescargarReporteEvaluacionesAsignaturasDocentePDFView(View):
    """Vista para que los docentes descarguen PDF de evaluaciones de sus asignaturas"""
    
    def get(self, request):
        # Verificar que sea docente
        if not (hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'docente')):
            return HttpResponseForbidden("No tienes permisos de docente")
        
        try:
            docente = request.user.usuario.docente
            
            # Obtener asignaturas que imparte el docente
            asignaturas_impartidas = AsignaturaImpartida.objects.filter(docente=docente)
            
            asignaturas_data = []
            
            for asignatura_impartida in asignaturas_impartidas:
                # Obtener clases de esta asignatura
                clases = Clase.objects.filter(asignatura_impartida=asignatura_impartida)
                
                # Obtener evaluaciones de todas las clases de esta asignatura
                evaluaciones = Evaluacion.objects.filter(clase__in=clases)
                total_evaluaciones = evaluaciones.count()
                
                if total_evaluaciones > 0:
                    # Obtener notas de estas evaluaciones
                    notas = AlumnoEvaluacion.objects.filter(evaluacion__in=evaluaciones)
                    total_notas = notas.count()
                    
                    if total_notas > 0:
                        promedio_asignatura = notas.aggregate(promedio=Avg('nota'))['promedio']
                        nota_maxima = notas.aggregate(max_nota=Max('nota'))['max_nota']
                        nota_minima = notas.aggregate(min_nota=Min('nota'))['min_nota']
                        aprobados = notas.filter(nota__gte=4.0).count()
                        reprobados = notas.filter(nota__lt=4.0).count()
                        porcentaje_aprobacion = (aprobados / total_notas * 100)
                        
                        # Estudiantes únicos evaluados
                        estudiantes_evaluados = notas.values('estudiante').distinct().count()
                        
                        # Estado según promedio
                        if promedio_asignatura >= 5.5:
                            estado = "Excelente"
                        elif promedio_asignatura >= 4.5:
                            estado = "Bueno"
                        elif promedio_asignatura >= 4.0:
                            estado = "Regular"
                        else:
                            estado = "Deficiente"
                    else:
                        promedio_asignatura = 0
                        nota_maxima = 0
                        nota_minima = 0
                        aprobados = 0
                        reprobados = 0
                        porcentaje_aprobacion = 0
                        estudiantes_evaluados = 0
                        estado = "Sin notas"
                else:
                    total_notas = 0
                    promedio_asignatura = 0
                    nota_maxima = 0
                    nota_minima = 0
                    aprobados = 0
                    reprobados = 0
                    porcentaje_aprobacion = 0
                    estudiantes_evaluados = 0
                    estado = "Sin evaluaciones"
                
                # Obtener cursos donde se imparte (para asignaturas regulares)
                cursos_str = []
                for clase in clases:
                    if clase.curso:
                        curso_nombre = f"{clase.curso.nivel}°{clase.curso.letra}"
                        if curso_nombre not in cursos_str:
                            cursos_str.append(curso_nombre)
                
                asignaturas_data.append({
                    'asignatura': asignatura_impartida.asignatura.nombre,
                    'codigo': asignatura_impartida.codigo,
                    'cursos': ', '.join(cursos_str) if cursos_str else 'Electivo',
                    'total_evaluaciones': total_evaluaciones,
                    'estudiantes_evaluados': estudiantes_evaluados,
                    'total_notas': total_notas,
                    'promedio_asignatura': round(promedio_asignatura, 2) if promedio_asignatura else 0,
                    'nota_maxima': nota_maxima if nota_maxima else 0,
                    'nota_minima': nota_minima if nota_minima else 0,
                    'aprobados': aprobados,
                    'reprobados': reprobados,
                    'porcentaje_aprobacion': round(porcentaje_aprobacion, 1) if porcentaje_aprobacion else 0,
                    'estado': estado
                })
            
            # Ordenar por promedio descendente
            asignaturas_data.sort(key=lambda x: x['promedio_asignatura'], reverse=True)
            
            # Calcular estadísticas generales
            if asignaturas_data:
                total_evaluaciones_general = sum(a['total_evaluaciones'] for a in asignaturas_data)
                total_notas_general = sum(a['total_notas'] for a in asignaturas_data)
                
                if total_notas_general > 0:
                    # Calcular promedio ponderado
                    suma_promedios = sum(a['promedio_asignatura'] * a['total_notas'] for a in asignaturas_data if a['total_notas'] > 0)
                    promedio_general = suma_promedios / total_notas_general
                    
                    total_aprobados_general = sum(a['aprobados'] for a in asignaturas_data)
                    porcentaje_aprobacion_general = (total_aprobados_general / total_notas_general * 100)
                else:
                    promedio_general = 0
                    porcentaje_aprobacion_general = 0
            else:
                total_evaluaciones_general = 0
                total_notas_general = 0
                promedio_general = 0
                porcentaje_aprobacion_general = 0
            
            # Preparar datos para el PDF
            data = {
                'docente': docente.usuario.get_full_name(),
                'asignaturas': asignaturas_data,
                'estadisticas_generales': {
                    'total_asignaturas': len(asignaturas_data),
                    'total_evaluaciones': total_evaluaciones_general,
                    'total_notas': total_notas_general,
                    'promedio_general': round(promedio_general, 2),
                    'porcentaje_aprobacion_general': round(porcentaje_aprobacion_general, 1)
                }
            }
            
            # Generar el PDF
            pdf_content = generar_pdf_evaluaciones_asignaturas_docente(data)
            
            # Crear respuesta HTTP
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="reporte_evaluaciones_asignaturas_docente_{docente.usuario.rut}.pdf"'
            
            return response
            
        except Exception as e:
            return HttpResponse(f"Error al generar el reporte: {str(e)}", status=500)

@method_decorator(login_required, name='dispatch')
class DescargarReporteEvaluacionesCursoJefePDFView(View):
    """Vista para que los profesores jefe descarguen PDF de evaluaciones de su curso"""
    
    def get(self, request):
        # Verificar que sea docente
        if not (hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'docente')):
            return HttpResponseForbidden("No tienes permisos de docente")
        
        try:
            docente = request.user.usuario.docente
            
            # Verificar si es profesor jefe
            profesor_jefe = ProfesorJefe.objects.filter(docente=docente).first()
            
            if not profesor_jefe or not profesor_jefe.curso:
                return HttpResponse("No eres profesor jefe de ningún curso", status=403)
            
            curso = profesor_jefe.curso
            
            # Obtener todas las asignaturas impartidas en el curso
            asignaturas_impartidas = AsignaturaImpartida.objects.filter(
                clases__curso=curso
            ).distinct()
            
            asignaturas_data = []
            
            for asignatura_impartida in asignaturas_impartidas:
                # Obtener evaluaciones de esta asignatura en el curso específico
                evaluaciones = Evaluacion.objects.filter(
                    clase__asignatura_impartida=asignatura_impartida,
                    clase__curso=curso
                )
                total_evaluaciones = evaluaciones.count()
                
                if total_evaluaciones > 0:
                    # Obtener notas de estudiantes del curso en estas evaluaciones
                    notas_curso = AlumnoEvaluacion.objects.filter(
                        evaluacion__in=evaluaciones,
                        estudiante__curso=curso
                    )
                    total_notas = notas_curso.count()
                    
                    if total_notas > 0:
                        promedio_asignatura = notas_curso.aggregate(promedio=Avg('nota'))['promedio']
                        nota_maxima = notas_curso.aggregate(max_nota=Max('nota'))['max_nota']
                        nota_minima = notas_curso.aggregate(min_nota=Min('nota'))['min_nota']
                        aprobados = notas_curso.filter(nota__gte=4.0).count()
                        reprobados = notas_curso.filter(nota__lt=4.0).count()
                        porcentaje_aprobacion = (aprobados / total_notas * 100)
                        
                        # Estudiantes evaluados
                        estudiantes_evaluados = notas_curso.values('estudiante').distinct().count()
                        
                        # Estado según promedio
                        if promedio_asignatura >= 5.5:
                            estado = "Excelente"
                        elif promedio_asignatura >= 4.5:
                            estado = "Bueno"
                        elif promedio_asignatura >= 4.0:
                            estado = "Regular"
                        else:
                            estado = "Deficiente"
                    else:
                        promedio_asignatura = 0
                        nota_maxima = 0
                        nota_minima = 0
                        aprobados = 0
                        reprobados = 0
                        porcentaje_aprobacion = 0
                        estudiantes_evaluados = 0
                        estado = "Sin notas"
                else:
                    total_notas = 0
                    promedio_asignatura = 0
                    nota_maxima = 0
                    nota_minima = 0
                    aprobados = 0
                    reprobados = 0
                    porcentaje_aprobacion = 0
                    estudiantes_evaluados = 0
                    estado = "Sin evaluaciones"
                
                # Información del docente
                docente_nombre = "Sin asignar"
                if asignatura_impartida.docente:
                    docente_nombre = asignatura_impartida.docente.usuario.get_full_name()
                
                asignaturas_data.append({
                    'asignatura': asignatura_impartida.asignatura.nombre,
                    'codigo': asignatura_impartida.codigo,
                    'docente': docente_nombre,
                    'total_evaluaciones': total_evaluaciones,
                    'estudiantes_evaluados': estudiantes_evaluados,
                    'total_notas': total_notas,
                    'promedio_asignatura': round(promedio_asignatura, 2) if promedio_asignatura else 0,
                    'nota_maxima': nota_maxima if nota_maxima else 0,
                    'nota_minima': nota_minima if nota_minima else 0,
                    'aprobados': aprobados,
                    'reprobados': reprobados,
                    'porcentaje_aprobacion': round(porcentaje_aprobacion, 1) if porcentaje_aprobacion else 0,
                    'estado': estado
                })
            
            # Ordenar por promedio descendente
            asignaturas_data.sort(key=lambda x: x['promedio_asignatura'], reverse=True)
            
            # Calcular estadísticas generales del curso
            if asignaturas_data:
                total_evaluaciones_curso = sum(a['total_evaluaciones'] for a in asignaturas_data)
                total_notas_curso = sum(a['total_notas'] for a in asignaturas_data)
                
                if total_notas_curso > 0:
                    # Calcular promedio ponderado del curso
                    suma_promedios = sum(a['promedio_asignatura'] * a['total_notas'] for a in asignaturas_data if a['total_notas'] > 0)
                    promedio_general_curso = suma_promedios / total_notas_curso
                    
                    total_aprobados_curso = sum(a['aprobados'] for a in asignaturas_data)
                    porcentaje_aprobacion_curso = (total_aprobados_curso / total_notas_curso * 100)
                else:
                    promedio_general_curso = 0
                    porcentaje_aprobacion_curso = 0
            else:
                total_evaluaciones_curso = 0
                total_notas_curso = 0
                promedio_general_curso = 0
                porcentaje_aprobacion_curso = 0
            
            # Obtener total de estudiantes del curso
            total_estudiantes_curso = curso.estudiantes.count()
            
            # Preparar datos para el PDF
            data = {
                'curso': f"{curso.nivel}°{curso.letra}",
                'curso_id': curso.id,
                'docente': docente.usuario.get_full_name(),
                'asignaturas': asignaturas_data,
                'estadisticas_generales': {
                    'total_estudiantes': total_estudiantes_curso,
                    'total_asignaturas': len(asignaturas_data),
                    'total_evaluaciones': total_evaluaciones_curso,
                    'total_notas': total_notas_curso,
                    'promedio_general_curso': round(promedio_general_curso, 2),
                    'porcentaje_aprobacion_curso': round(porcentaje_aprobacion_curso, 1)
                }
            }
            
            # Generar el PDF
            pdf_content = generar_pdf_evaluaciones_curso_jefe(data)
            
            # Crear respuesta HTTP
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="reporte_evaluaciones_curso_{curso.nivel}{curso.letra}_jefe_{docente.usuario.rut}.pdf"'
            
            return response
            
        except Exception as e:
            return HttpResponse(f"Error al generar el reporte: {str(e)}", status=500) 

@method_decorator(login_required, name='dispatch')
class DescargarReporteAsistenciaAsignaturasDocentePDFView(View):
    """Vista para descargar PDF del reporte de asistencia de asignaturas del docente"""
    
    def get(self, request):
        # Verificar que sea docente
        if not (hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'docente')):
            return HttpResponse('No tienes permisos de docente', status=403)
        
        try:
            # Obtener datos del reporte
            from Core.views.docentes import ReporteAsistenciaAsignaturasDocenteView
            vista_reporte = ReporteAsistenciaAsignaturasDocenteView()
            vista_reporte.request = request
            
            response_data = vista_reporte.get(request)
            if hasattr(response_data, 'content'):
                import json
                data = json.loads(response_data.content.decode('utf-8'))
            else:
                data = response_data
            
            if not data.get('success'):
                return HttpResponse('Error al obtener datos del reporte', status=400)
            
            # Generar PDF
            pdf_buffer = generar_pdf_asistencia_asignaturas_docente(data)
            
            # Configurar respuesta
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            fecha_actual = timezone.now().strftime('%Y%m%d_%H%M')
            filename = f'reporte_asistencia_asignaturas_docente_{fecha_actual}.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            return HttpResponse(f'Error al generar PDF: {str(e)}', status=500)

@method_decorator(login_required, name='dispatch')
class DescargarReporteAsistenciaCursoJefePDFView(View):
    """Vista para descargar PDF del reporte de asistencia del curso jefe"""
    
    def get(self, request):
        # Verificar que sea docente
        if not (hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'docente')):
            return HttpResponse('No tienes permisos de docente', status=403)
        
        try:
            # Obtener datos del reporte
            from Core.views.docentes import ReporteAsistenciaCursoJefeView
            vista_reporte = ReporteAsistenciaCursoJefeView()
            vista_reporte.request = request
            
            response_data = vista_reporte.get(request)
            if hasattr(response_data, 'content'):
                import json
                data = json.loads(response_data.content.decode('utf-8'))
            else:
                data = response_data
            
            if not data.get('success'):
                return HttpResponse('Error al obtener datos del reporte', status=400)
            
            # Generar PDF
            pdf_buffer = generar_pdf_asistencia_curso_jefe(data)
            
            # Configurar respuesta
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            fecha_actual = timezone.now().strftime('%Y%m%d_%H%M')
            filename = f'reporte_asistencia_curso_jefe_{fecha_actual}.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            return HttpResponse(f'Error al generar PDF: {str(e)}', status=500)

@method_decorator(csrf_exempt, name='dispatch')
class DescargarAnalisisIAPDFView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            pdf_buffer = generar_pdf_analisis_ia(data)
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="analisis_ia.pdf"'
            return response
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})