from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views import View
from Core.models import Estudiante, Curso, Asistencia, AlumnoEvaluacion
from Core.views.alumnos import get_horario_estudiante, get_asistencia_estudiante, get_evaluaciones_estudiante, get_promedio_estudiante
from .pdf_generators import generar_pdf_horario, generar_pdf_asistencia, generar_pdf_calificaciones
from django.db.models import Avg
from datetime import date, datetime
from Core.views.reportes_simple import get_periodo_fechas
from .pdf_generators import generar_pdf_reporte_estudiantes_riesgo

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
                        'id': estudiante.id,
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