from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from Core.models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura, AsignaturaImpartida, Curso, ProfesorJefe, Evaluacion, AlumnoEvaluacion, EvaluacionBase, ClaseCancelada, Comunicacion
from django.db.models import Count, Avg, Max, Min
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
from datetime import date, timedelta, datetime, time
import json
from collections import defaultdict

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

def get_eventos_calendario_docente(docente_id):
    """
    Obtiene los eventos del calendario para un docente.
    Incluye eventos del colegio, de las asignaturas que imparte y las clases canceladas.
    """
    try:
        docente = Docente.objects.get(pk=docente_id)
        
        # Obtener IDs de asignaturas que imparte el docente
        asignaturas_ids = AsignaturaImpartida.objects.filter(
            docente=docente
        ).values_list('asignatura_id', flat=True)

        eventos = []
        
        # Eventos del colegio
        eventos_colegio = CalendarioColegio.objects.all()
        for evento in eventos_colegio:
            # Verificar si el docente es el encargado (tiene autoridad)
            nombre_completo = f"{docente.usuario.nombre} {docente.usuario.apellido_paterno}"
            es_encargado = nombre_completo.lower() in evento.encargado.lower()
            
            eventos.append({
                'id': f'colegio_{evento.pk}',
                'title': evento.nombre_actividad,
                'start': f'{evento.fecha}T{evento.hora}',
                'description': evento.descripcion,
                'color': '#0dcaf0',  # Azul claro para eventos del colegio
                'extendedProps': {
                    'type': 'Colegio',
                    'encargado': evento.encargado,
                    'ubicacion': evento.ubicacion,
                    'puede_editar': es_encargado,
                    'puede_eliminar': es_encargado
                }
            })

        # Eventos de las clases del docente
        eventos_clase = CalendarioClase.objects.filter(
            asignatura_id__in=list(asignaturas_ids)
        )
        for evento in eventos_clase:
            # El docente siempre puede editar/eliminar sus propios eventos de clase
            # ya que solo aparecen los eventos de sus asignaturas impartidas
            eventos.append({
                'id': f'clase_{evento.pk}',
                'title': f"{evento.nombre_actividad} - {evento.asignatura.nombre}",
                'start': f'{evento.fecha}T{evento.hora if evento.hora else "00:00:00"}',
                'description': evento.descripcion,
                'color': '#198754',  # Verde para evaluaciones
                'extendedProps': {
                    'type': 'Asignatura',
                    'materia': evento.asignatura.nombre,
                    'puede_editar': True,
                    'puede_eliminar': True
                }
            })
        
        # Clases canceladas del docente
        clases_canceladas = ClaseCancelada.objects.filter(docente=docente)
        for cancelacion in clases_canceladas:
            # El docente puede editar/eliminar sus propias cancelaciones
            eventos.append({
                'id': f'cancelada_{cancelacion.pk}',
                'title': f"CANCELADA: {cancelacion.asignatura_impartida.asignatura.nombre}",
                'start': f'{cancelacion.fecha_cancelacion}T{cancelacion.hora_cancelacion}',
                'description': f"Motivo: {cancelacion.get_motivo_display()}. {cancelacion.descripcion or ''}",
                'color': '#dc3545',  # Rojo para clases canceladas
                'extendedProps': {
                    'type': 'Cancelacion',
                    'motivo': cancelacion.get_motivo_display(),
                    'recuperada': cancelacion.clase_recuperada,
                    'fecha_recuperacion': cancelacion.fecha_recuperacion,
                    'puede_editar': True,
                    'puede_eliminar': True
                }
            })

        return eventos

    except Docente.DoesNotExist:
        return []

def get_eventos_proximos_docente(docente_id):
    """
    Obtiene los próximos eventos para mostrar en HTML estático
    """
    from datetime import datetime, timedelta
    
    try:
        docente = Docente.objects.get(pk=docente_id)
        
        # Obtener IDs de asignaturas que imparte el docente
        asignaturas_ids = AsignaturaImpartida.objects.filter(
            docente=docente
        ).values_list('asignatura_id', flat=True)

        eventos_proximos = []
        hoy = datetime.now().date()
        
        # Eventos del colegio próximos
        eventos_colegio = CalendarioColegio.objects.filter(
            fecha__gte=hoy
        ).order_by('fecha', 'hora')[:5]
        
        for evento in eventos_colegio:
            dias_restantes = (evento.fecha - hoy).days
            eventos_proximos.append({
                'titulo': evento.nombre_actividad,
                'descripcion': evento.descripcion,
                'fecha': evento.fecha,
                'hora': evento.hora,
                'tipo': 'Colegio',
                'dias_restantes': dias_restantes,
                'ubicacion': evento.ubicacion
            })

        # Eventos de las clases del docente próximos
        eventos_clase = CalendarioClase.objects.filter(
            asignatura_id__in=list(asignaturas_ids),
            fecha__gte=hoy
        ).order_by('fecha', 'hora')[:5]
        
        for evento in eventos_clase:
            dias_restantes = (evento.fecha - hoy).days
            eventos_proximos.append({
                'titulo': f"{evento.nombre_actividad} - {evento.asignatura.nombre}",
                'descripcion': evento.descripcion,
                'fecha': evento.fecha,
                'hora': evento.hora or datetime.now().time(),
                'tipo': 'Asignatura',
                'dias_restantes': dias_restantes,
                'materia': evento.asignatura.nombre
            })
        
        # Clases canceladas próximas
        clases_canceladas = ClaseCancelada.objects.filter(
            docente=docente,
            fecha_cancelacion__gte=hoy
        ).order_by('fecha_cancelacion', 'hora_cancelacion')[:3]
        
        for cancelacion in clases_canceladas:
            dias_restantes = (cancelacion.fecha_cancelacion - hoy).days
            eventos_proximos.append({
                'titulo': f"CANCELADA: {cancelacion.asignatura_impartida.asignatura.nombre}",
                'descripcion': f"Motivo: {cancelacion.get_motivo_display()}. {cancelacion.descripcion or ''}",
                'fecha': cancelacion.fecha_cancelacion,
                'hora': cancelacion.hora_cancelacion,
                'tipo': 'Cancelacion',
                'dias_restantes': dias_restantes
            })

        # Ordenar todos los eventos por fecha y hora
        eventos_proximos.sort(key=lambda x: (x['fecha'], x['hora']))
        
        return eventos_proximos[:12]  # Máximo 12 eventos

    except Docente.DoesNotExist:
        return []

def get_clases_canceladas_docente(docente_id):
    """
    Obtiene las clases canceladas por el docente
    """
    clases_canceladas = ClaseCancelada.objects.filter(
        docente_id=docente_id
    ).select_related(
        'asignatura_impartida__asignatura',
        'asignatura_impartida__docente__usuario'
    ).order_by('-fecha_cancelacion')
    
    return clases_canceladas

def get_comunicaciones_docente(docente):
    """
    Obtiene todas las comunicaciones relacionadas con un docente
    """
    from django.db import models
    
    # Obtener cursos donde el docente imparte asignaturas o es profesor jefe
    cursos_docente = set()
    
    # Cursos donde imparte asignaturas
    asignaturas_impartidas = AsignaturaImpartida.objects.filter(docente=docente)
    for asignatura in asignaturas_impartidas:
        clases = Clase.objects.filter(asignatura_impartida=asignatura)
        for clase in clases:
            if clase.curso:
                cursos_docente.add(clase.curso.id)
    
    # Cursos donde es profesor jefe
    try:
        profesor_jefe = ProfesorJefe.objects.filter(docente=docente)
        for pj in profesor_jefe:
            cursos_docente.add(pj.curso.id)
    except:
        pass
    
    # Obtener comunicaciones
    # Obtener el AuthUser asociado al docente a través de la relación Usuario -> AuthUser
    auth_user = docente.usuario.auth_user
    
    comunicaciones = Comunicacion.objects.filter(
        models.Q(autor=auth_user) |  # Comunicaciones que envió
        models.Q(destinatarios_cursos__id__in=cursos_docente) |  # Para sus cursos
        models.Q(destinatarios_usuarios=auth_user)  # Dirigidas a él específicamente
    ).distinct().select_related('autor').prefetch_related(
        'destinatarios_cursos', 'adjuntos'
    ).order_by('-fecha_envio')
    
    # Estadísticas
    total = comunicaciones.count()
    enviadas = comunicaciones.filter(autor=auth_user).count()
    recibidas = total - enviadas
    con_adjuntos = comunicaciones.filter(adjuntos__isnull=False).distinct().count()
    
    return {
        'comunicaciones': comunicaciones,
        'total': total,
        'enviadas': enviadas,
        'recibidas': recibidas,
        'con_adjuntos': con_adjuntos
    }

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
        
        # Calcular estadísticas reales para cada curso
        cursos_con_estadisticas = []
        for curso in cursos_profesor_jefe:
            # Calcular asistencia promedio del curso
            asistencias_curso = Asistencia.objects.filter(estudiante__curso=curso)
            if asistencias_curso.exists():
                total_asistencias = asistencias_curso.count()
                presentes = asistencias_curso.filter(presente=True).count()
                porcentaje_asistencia = round((presentes / total_asistencias * 100), 1) if total_asistencias > 0 else 0
            else:
                porcentaje_asistencia = 0
            
            # Calcular promedio general del curso
            evaluaciones_curso = Evaluacion.objects.filter(clase__curso=curso)
            if evaluaciones_curso.exists():
                notas_curso = AlumnoEvaluacion.objects.filter(
                    evaluacion__in=evaluaciones_curso,
                    estudiante__curso=curso
                )
                promedio_general = notas_curso.aggregate(promedio=Avg('nota'))['promedio']
                promedio_general = round(promedio_general, 1) if promedio_general else 0.0
            else:
                promedio_general = 0.0
            
            # Contar asignaturas del curso
            total_asignaturas = AsignaturaImpartida.objects.filter(
                clases__curso=curso
            ).distinct().count()
            
            # Agregar estadísticas al curso
            curso.porcentaje_asistencia = porcentaje_asistencia
            curso.promedio_general = promedio_general
            curso.total_asignaturas = total_asignaturas
            
            cursos_con_estadisticas.append(curso)
        
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
        
        # Obtener eventos del calendario y clases canceladas
        eventos_calendario_lista = get_eventos_calendario_docente(docente.pk)
        eventos_calendario = json.dumps(eventos_calendario_lista)  # Para el JavaScript
        eventos_proximos = get_eventos_proximos_docente(docente.pk)  # Para HTML estático
        clases_canceladas = get_clases_canceladas_docente(docente.pk)
        
        # Obtener comunicaciones del docente
        datos_comunicaciones = get_comunicaciones_docente(docente)
        
        # Obtener todos los cursos para filtros
        cursos = Curso.objects.all().order_by('nivel', 'letra')
        
        context = {
            'docente': docente,  # Agregar información del docente
            'cursos_profesor_jefe': cursos_con_estadisticas,
            'asignaturas': asignaturas,
            'evaluaciones_docente': evaluaciones_docente,
            'estadisticas_docente': estadisticas_docente,
            'estadisticas_asistencia': estadisticas_asistencia,
            'eventos_calendario': eventos_calendario,
            'eventos_proximos': eventos_proximos,  # Eventos para HTML estático
            'clases_canceladas': clases_canceladas,
            'comunicaciones': datos_comunicaciones['comunicaciones'],
            'comunicaciones_stats': {
                'total': datos_comunicaciones['total'],
                'enviadas': datos_comunicaciones['enviadas'],
                'recibidas': datos_comunicaciones['recibidas'],
                'con_adjuntos': datos_comunicaciones['con_adjuntos']
            },
            'cursos': cursos
        }
        return render(request, 'teacher_panel_modular.html', context)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class CancelarClaseView(View):
    def post(self, request):
        if not hasattr(request.user.usuario, 'docente'):
            return JsonResponse({'success': False, 'error': 'No tienes permiso para cancelar clases'})
        
        try:
            data = json.loads(request.body)
            docente = request.user.usuario.docente
            
            # Validar datos requeridos
            asignatura_impartida_id = data.get('asignatura_impartida_id')
            fecha_cancelacion = data.get('fecha_cancelacion')
            hora_cancelacion = data.get('hora_cancelacion')
            motivo = data.get('motivo')
            descripcion = data.get('descripcion', '')
            
            if not all([asignatura_impartida_id, fecha_cancelacion, hora_cancelacion, motivo]):
                return JsonResponse({'success': False, 'error': 'Faltan datos requeridos'})
            
            # Verificar que la asignatura pertenezca al docente
            asignatura_impartida = AsignaturaImpartida.objects.filter(
                id=asignatura_impartida_id,
                docente=docente
            ).first()
            
            if not asignatura_impartida:
                return JsonResponse({'success': False, 'error': 'No tienes permiso para cancelar esta asignatura'})
            
            # Verificar que no exista ya una cancelación para esta fecha y hora
            cancelacion_existente = ClaseCancelada.objects.filter(
                asignatura_impartida=asignatura_impartida,
                fecha_cancelacion=fecha_cancelacion,
                hora_cancelacion=hora_cancelacion
            ).exists()
            
            if cancelacion_existente:
                return JsonResponse({'success': False, 'error': 'Ya existe una cancelación para esta fecha y hora'})
            
            # Crear la cancelación
            cancelacion = ClaseCancelada.objects.create(
                docente=docente,
                asignatura_impartida=asignatura_impartida,
                fecha_cancelacion=fecha_cancelacion,
                hora_cancelacion=hora_cancelacion,
                motivo=motivo,
                descripcion=descripcion
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Clase cancelada exitosamente',
                'cancelacion_id': cancelacion.pk
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class MarcarClaseRecuperadaView(View):
    def post(self, request):
        if not hasattr(request.user.usuario, 'docente'):
            return JsonResponse({'success': False, 'error': 'No tienes permiso'})
        
        try:
            data = json.loads(request.body)
            docente = request.user.usuario.docente
            
            cancelacion_id = data.get('cancelacion_id')
            fecha_recuperacion = data.get('fecha_recuperacion')
            
            if not cancelacion_id:
                return JsonResponse({'success': False, 'error': 'ID de cancelación requerido'})
            
            # Verificar que la cancelación pertenezca al docente
            cancelacion = ClaseCancelada.objects.filter(
                id=cancelacion_id,
                docente=docente
            ).first()
            
            if not cancelacion:
                return JsonResponse({'success': False, 'error': 'Cancelación no encontrada'})
            
            # Marcar como recuperada
            cancelacion.clase_recuperada = True
            if fecha_recuperacion:
                cancelacion.fecha_recuperacion = fecha_recuperacion
            cancelacion.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Clase marcada como recuperada'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ObtenerHorariosAsignaturaView(View):
    def get(self, request, asignatura_id):
        if not hasattr(request.user.usuario, 'docente'):
            return JsonResponse({'success': False, 'error': 'No tienes permiso'})
        
        try:
            docente = request.user.usuario.docente
            
            # Verificar que la asignatura pertenezca al docente
            asignatura_impartida = AsignaturaImpartida.objects.filter(
                id=asignatura_id,
                docente=docente
            ).select_related('asignatura').first()
            
            if not asignatura_impartida:
                return JsonResponse({'success': False, 'error': 'Asignatura no encontrada o no autorizada'})
            
            # Obtener todas las clases de esta asignatura
            clases = Clase.objects.filter(
                asignatura_impartida=asignatura_impartida
            ).select_related('curso').order_by('fecha', 'horario')
            
            # Mapeo de bloques a horas
            mapeo_bloques = {
                '1': ('08:00', '08:45'),
                '2': ('08:45', '09:30'),
                '3': ('09:45', '10:30'),
                '4': ('10:30', '11:15'),
                '5': ('11:30', '12:15'),
                '6': ('12:15', '13:00'),
                '7': ('13:45', '14:30'),
                '8': ('14:30', '15:15'),
                '9': ('15:15', '16:00'),
            }
            
            # Agrupar clases por día y bloques consecutivos
            horarios_agrupados = {}
            for clase in clases:
                dia = clase.fecha
                bloque = str(clase.horario)
                sala = clase.get_sala_display() if hasattr(clase, 'get_sala_display') else clase.sala
                curso = str(clase.curso) if clase.curso else 'Electivo'
                
                if dia not in horarios_agrupados:
                    horarios_agrupados[dia] = []
                
                # Si hay bloques anteriores y son consecutivos, extender el último bloque
                if horarios_agrupados[dia] and int(bloque) == int(horarios_agrupados[dia][-1]['bloque_fin']) + 1:
                    horarios_agrupados[dia][-1]['bloque_fin'] = bloque
                    horarios_agrupados[dia][-1]['hora_fin'] = mapeo_bloques[bloque][1]
                else:
                    horarios_agrupados[dia].append({
                        'bloque_inicio': bloque,
                        'bloque_fin': bloque,
                        'hora_inicio': mapeo_bloques[bloque][0],
                        'hora_fin': mapeo_bloques[bloque][1],
                        'sala': sala,
                        'curso': curso
                    })
            
            # Convertir el diccionario a lista y formatear la salida
            horarios = []
            for dia, bloques in horarios_agrupados.items():
                for bloque in bloques:
                    horarios.append({
                        'dia': dia,
                        'bloque': f"{bloque['bloque_inicio']}-{bloque['bloque_fin']}" if bloque['bloque_inicio'] != bloque['bloque_fin'] else bloque['bloque_inicio'],
                        'horario': f"{bloque['hora_inicio']} - {bloque['hora_fin']}",
                        'sala': bloque['sala'],
                        'curso': bloque['curso']
                    })
            
            return JsonResponse({
                'success': True,
                'horarios': horarios,
                'asignatura': asignatura_impartida.asignatura.nombre,
                'codigo': asignatura_impartida.codigo
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ObtenerAsistenciaAsignaturaView(View):
    def get(self, request, asignatura_id):
        if not hasattr(request.user.usuario, 'docente'):
            return JsonResponse({'success': False, 'error': 'No tienes permiso'})
        
        try:
            docente = request.user.usuario.docente
            
            # Verificar que la asignatura pertenezca al docente
            asignatura_impartida = AsignaturaImpartida.objects.filter(
                id=asignatura_id,
                docente=docente
            ).select_related('asignatura').first()
            
            if not asignatura_impartida:
                return JsonResponse({'success': False, 'error': 'Asignatura no encontrada o no autorizada'})
            
            # Obtener la fecha actual
            now = timezone.localtime(timezone.now())
            hoy = now.date()
            
            # Si es después de medianoche pero antes de las 3 AM, usar la fecha de ayer
            if now.hour < 3:
                hoy = hoy - timedelta(days=1)
            
            # Obtener el día de la semana en español
            dia_semana = hoy.strftime('%A').upper()
            mapeo_dias = {
                'MONDAY': 'LUNES',
                'TUESDAY': 'MARTES',
                'WEDNESDAY': 'MIERCOLES',
                'THURSDAY': 'JUEVES',
                'FRIDAY': 'VIERNES',
                'SATURDAY': 'SABADO',
                'SUNDAY': 'DOMINGO'
            }
            dia_semana = mapeo_dias.get(dia_semana)
            
            # Verificar si hay clases programadas para hoy
            clases_hoy = Clase.objects.filter(
                asignatura_impartida=asignatura_impartida,
                fecha=dia_semana
            ).select_related('curso').order_by('horario')
            
            # Si no hay clases hoy, buscar la próxima clase disponible
            if not clases_hoy.exists():
                # Mapeo de días de la semana a números (0 = Lunes, 6 = Domingo)
                dias_semana = {
                    'LUNES': 0,
                    'MARTES': 1,
                    'MIERCOLES': 2,
                    'JUEVES': 3,
                    'VIERNES': 4,
                    'SABADO': 5,
                    'DOMINGO': 6
                }
                
                # Obtener el número del día actual
                dia_actual = dias_semana[dia_semana]
                
                # Buscar la próxima clase
                for i in range(1, 8):  # Buscar en los próximos 7 días
                    proximo_dia = (dia_actual + i) % 7
                    for dia, num in dias_semana.items():
                        if num == proximo_dia:
                            clases_siguiente = Clase.objects.filter(
                                asignatura_impartida=asignatura_impartida,
                                fecha=dia
                            ).select_related('curso').order_by('horario')
                            if clases_siguiente.exists():
                                clases_hoy = clases_siguiente
                                # Ajustar la fecha al próximo día con clases
                                dias_hasta_siguiente = i
                                hoy = hoy + timedelta(days=dias_hasta_siguiente)
                                dia_semana = hoy.strftime('%A').upper()
                                dia_semana = mapeo_dias.get(dia_semana)
                                break
                    if clases_hoy.exists():
                        break
            
            # Si no se encontraron clases en los próximos 7 días
            if not clases_hoy.exists():
                return JsonResponse({
                    'success': False,
                    'error': 'No hay clases programadas para los próximos días'
                })
            
            # Crear datetime para inicio y fin del día
            inicio_dia = datetime.combine(hoy, time.min)
            fin_dia = datetime.combine(hoy, time.max)
            
            # Hacer consciente de zona horaria
            inicio_dia = timezone.make_aware(inicio_dia)
            fin_dia = timezone.make_aware(fin_dia)
            
            # Organizar datos por curso
            clases_por_curso = {}
            
            for clase in clases_hoy:
                if clase.curso:
                    curso_id = clase.curso_id
                    curso_nombre = str(clase.curso)
                    estudiantes = clase.curso.estudiantes.all().select_related('usuario')
                else:
                    curso_id = 'ELECTIVO'
                    curso_nombre = 'Electivo'
                    estudiantes = Estudiante.objects.filter(
                        asignaturas_inscritas__asignatura_impartida=asignatura_impartida
                    ).select_related('usuario')
                
                if curso_id not in clases_por_curso:
                    clases_por_curso[curso_id] = {
                        'curso': curso_nombre,
                        'clases': [],
                        'estudiantes': []
                    }
                
                clases_por_curso[curso_id]['clases'].append({
                    'id': clase.id,
                    'horario': clase.horario,
                    'sala': clase.get_sala_display() if hasattr(clase, 'get_sala_display') else clase.sala,
                })
                
                if not clases_por_curso[curso_id]['estudiantes']:
                    if not estudiantes.exists():
                        continue
                    
                    # Obtener asistencias existentes para todas las clases de hoy
                    asistencias = Asistencia.objects.filter(
                        clase__in=clases_hoy,
                        estudiante__in=estudiantes,
                        fecha_registro__range=(inicio_dia, fin_dia)
                    ).select_related('estudiante', 'clase')
                    
                    # Crear diccionario para acceso rápido
                    asistencias_dict = {}
                    for asistencia in asistencias:
                        key = f"{asistencia.estudiante.usuario.auth_user_id}_{asistencia.clase_id}"
                        asistencias_dict[key] = asistencia
                    
                    # Preparar datos de estudiantes con su asistencia
                    estudiantes_data = []
                    for estudiante in estudiantes:
                        asistencias_estudiante = []
                        for clase in clases_hoy:
                            key = f"{estudiante.usuario.auth_user_id}_{clase.id}"
                            asistencia = asistencias_dict.get(key)
                            asistencias_estudiante.append({
                                'clase_id': clase.id,
                                'presente': asistencia.presente if asistencia else None,
                                'justificado': asistencia.justificado if asistencia else False,
                                'observacion': asistencia.observaciones if asistencia else ''
                            })
                        
                        estudiantes_data.append({
                            'id': estudiante.usuario.auth_user_id,
                            'nombre': f"{estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}",
                            'rut': f"{estudiante.usuario.rut}-{estudiante.usuario.div}",
                            'asistencias': asistencias_estudiante
                        })
                    
                    clases_por_curso[curso_id]['estudiantes'] = estudiantes_data
            
            # Convertir el diccionario a lista y filtrar cursos sin estudiantes
            datos_cursos = [curso_data for curso_data in clases_por_curso.values() if curso_data['estudiantes']]
            
            # Si no hay cursos con estudiantes
            if not datos_cursos:
                return JsonResponse({
                    'success': False,
                    'error': 'No hay estudiantes registrados en los cursos o inscritos en el electivo'
                })
            
            # Calcular estadísticas por curso
            for curso_data in datos_cursos:
                total_estudiantes = len(curso_data['estudiantes'])
                presentes = 0
                ausentes = 0
                sin_registro = 0
                
                # Primero, verificar si hay al menos una asistencia registrada para cada estudiante
                for estudiante in curso_data['estudiantes']:
                    tiene_registro = False
                    es_presente = False
                    es_ausente = False
                    
                    for asistencia in estudiante['asistencias']:
                        if asistencia['presente'] is not None:
                            tiene_registro = True
                            if asistencia['presente']:
                                es_presente = True
                            else:
                                es_ausente = True
                    
                    if tiene_registro:
                        if es_presente:
                            presentes += 1
                        elif es_ausente:
                            ausentes += 1
                    else:
                        sin_registro += 1
                
                # Calcular estado de asistencia
                if sin_registro == 0:  # Asistencia completa
                    estado = 'completo'
                    estado_texto = 'Asistencia Completa'
                elif sin_registro == total_estudiantes:  # Sin registros
                    estado = 'pendiente'
                    estado_texto = 'Sin Registros'
                else:  # Asistencia parcial
                    estado = 'parcial'
                    estado_texto = 'Asistencia Parcial'
                
                curso_data.update({
                    'total_estudiantes': total_estudiantes,
                    'presentes': presentes,
                    'ausentes': ausentes,
                    'sin_registro': sin_registro,
                    'estado': estado,
                    'estado_texto': estado_texto
                })
            
            return JsonResponse({
                'success': True,
                'asignatura': asignatura_impartida.asignatura.nombre,
                'codigo': asignatura_impartida.codigo,
                'fecha': hoy.strftime('%Y-%m-%d'),
                'dia_semana': dia_semana,
                'cursos': datos_cursos
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class GuardarAsistenciaView(View):
    def post(self, request, clase_id):
        if not hasattr(request.user.usuario, 'docente'):
                return JsonResponse({
                    'success': False,
                'error': 'No tienes permiso para registrar asistencia'
            })
        
        try:
            # Obtener el docente
            docente = request.user.usuario.docente
            
            # Obtener y validar la clase
            try:
                clase = get_object_or_404(
                    Clase.objects.select_related(
                        'asignatura_impartida__asignatura',
                        'asignatura_impartida__docente',
                        'curso'
                    ), 
                    id=clase_id,
                    asignatura_impartida__docente=docente
                )
            except Clase.DoesNotExist:
                    return JsonResponse({
                    'success': False,
                    'error': 'Clase no encontrada o no tienes permiso para registrar asistencia'
                })
            
            # Verificar fecha y hora
            now = timezone.now()
            fecha_registro = now.date()
            
            # Si es después de medianoche pero antes de las 3 AM, usar la fecha de ayer
            if now.hour < 3:
                fecha_registro = fecha_registro - timezone.timedelta(days=1)
            
            # Obtener el día de la semana en español
            dia_semana = fecha_registro.strftime('%A').upper()
            mapeo_dias = {
                'MONDAY': 'LUNES',
                'TUESDAY': 'MARTES',
                'WEDNESDAY': 'MIERCOLES',
                'THURSDAY': 'JUEVES',
                'FRIDAY': 'VIERNES',
                'SATURDAY': 'SABADO',
                'SUNDAY': 'DOMINGO'
            }
            dia_semana = mapeo_dias.get(dia_semana)
            
            # Validar día de la clase
            if clase.fecha != dia_semana:
                dias_semana = {
                    'LUNES': 0, 'MARTES': 1, 'MIERCOLES': 2,
                    'JUEVES': 3, 'VIERNES': 4, 'SABADO': 5, 'DOMINGO': 6
                }
                
                dia_actual = dias_semana[dia_semana]
                dia_clase = dias_semana[clase.fecha]
                
                dias_hasta_clase = (dia_clase - dia_actual) % 7
                if dias_hasta_clase == 0:
                    hora_actual = now.strftime('%H:%M')
                    if hora_actual > clase.horario.split('-')[1]:
                        return JsonResponse({
                            'success': False,
                            'error': 'No se puede registrar asistencia para una clase que ya pasó'
                        })
                
                fecha_registro = fecha_registro + timezone.timedelta(days=dias_hasta_clase)
            
            # Obtener y validar datos del request
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Formato de datos inválido'
                })
                
            # Validar que sea una lista de asistencias
            if not isinstance(data, list):
                return JsonResponse({
                    'success': False,
                    'error': 'Formato de datos inválido: se espera una lista de asistencias'
                })
            
            # Procesar asistencias en lote
            errores = []
            asistencias_procesadas = 0
            
            # Obtener estudiantes válidos según el tipo de clase
            if clase.curso:
                estudiantes_validos = Estudiante.objects.filter(
                    curso=clase.curso
                ).select_related('usuario')
            else:
                estudiantes_validos = Estudiante.objects.filter(
                    asignaturas_inscritas__asignatura_impartida=clase.asignatura_impartida,
                    asignaturas_inscritas__validada=True
                ).select_related('usuario')
            
            # Crear un diccionario para acceso rápido
            estudiantes_dict = {
                str(estudiante.usuario.auth_user_id): estudiante 
                for estudiante in estudiantes_validos
            }
            
            # Obtener todas las asistencias existentes para esta clase
            asistencias_existentes = {
                (a.clase_id, a.estudiante.usuario.auth_user_id): a 
                for a in Asistencia.objects.filter(clase=clase).select_related('estudiante__usuario')
            }
            
            for asistencia_data in data:
                try:
                    estudiante_id = str(asistencia_data.get('estudiante_id'))
                    
                    # Validar datos requeridos
                    if not all(key in asistencia_data for key in ['presente', 'justificado']):
                        errores.append({
                            'estudiante_id': estudiante_id,
                            'error': "Datos incompletos",
                            'detalles': f"Faltan campos requeridos: presente y/o justificado"
                        })
                        continue
                    
                    # Obtener estudiante del diccionario
                    estudiante = estudiantes_dict.get(estudiante_id)
                    if not estudiante:
                        errores.append({
                            'estudiante_id': estudiante_id,
                            'error': "Estudiante no encontrado",
                            'detalles': "El estudiante no está inscrito en este curso/asignatura"
                        })
                        continue
                    
                    # Buscar asistencia existente
                    asistencia_existente = asistencias_existentes.get((clase.id, estudiante.usuario.auth_user_id))
                    
                    if asistencia_existente:
                        # Actualizar asistencia existente
                        asistencia_existente.presente = asistencia_data['presente']
                        asistencia_existente.justificado = asistencia_data['justificado']
                        asistencia_existente.observaciones = asistencia_data.get('observaciones', '')
                        asistencia_existente.fecha_registro = now
                        asistencia_existente.save()
                    else:
                        # Crear nueva asistencia
                        Asistencia.objects.create(
                            clase=clase,
                            estudiante=estudiante,
                            presente=asistencia_data['presente'],
                            justificado=asistencia_data['justificado'],
                            observaciones=asistencia_data.get('observaciones', ''),
                            fecha_registro=now
                        )
                    
                    asistencias_procesadas += 1
                    
                except Exception as e:
                    errores.append({
                        'estudiante_id': estudiante_id,
                        'error': "Error al procesar asistencia",
                        'detalles': str(e)
                    })
            
            # Si hay errores, reportarlos junto con un resumen
            if errores:
                return JsonResponse({
                    'success': False,
                    'error': 'Errores al procesar algunos estudiantes',
                    'resumen': f'Se procesaron {asistencias_procesadas} asistencias correctamente. {len(errores)} registros tuvieron errores.',
                    'errores': errores
                })
            
            return JsonResponse({
                'success': True,
                'message': f'Se procesaron {asistencias_procesadas} asistencias correctamente'
            })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al guardar las asistencias: {str(e)}',
                'detalles': str(e)
            })

@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ObtenerHistorialAsistenciaView(View):
    def get(self, request, asignatura_id):
        if not hasattr(request.user.usuario, 'docente'):
            return JsonResponse({'success': False, 'error': 'No tienes permiso'})
            
        try:
            docente = request.user.usuario.docente
            
            # Verificar que la asignatura pertenezca al docente
            asignatura_impartida = AsignaturaImpartida.objects.filter(
                id=asignatura_id,
                docente=docente
            ).first()
            
            if not asignatura_impartida:
                return JsonResponse({'success': False, 'error': 'Asignatura no encontrada o no autorizada'})
            
            # Obtener los filtros
            mes = request.GET.get('mes')
            estado = request.GET.get('estado')
            estudiante_id = request.GET.get('estudiante')
            
            # Construir el query base
            asistencias = Asistencia.objects.filter(
                clase__asignatura_impartida=asignatura_impartida
            ).select_related(
                'estudiante__usuario',
                'clase'
            ).order_by('-fecha_registro')
            
            # Aplicar filtros
            if mes:
                asistencias = asistencias.filter(fecha_registro__month=mes)
            
            if estado:
                asistencias = asistencias.filter(presente=(estado == 'presente'))
            
            if estudiante_id:
                asistencias = asistencias.filter(estudiante__usuario__auth_user_id=estudiante_id)
            
            # Preparar los datos para la respuesta
            asistencias_data = []
            for asistencia in asistencias:
                asistencias_data.append({
                    'fecha_registro': asistencia.fecha_registro.isoformat(),
                    'estudiante_nombre': f"{asistencia.estudiante.usuario.nombre} {asistencia.estudiante.usuario.apellido_paterno}",
                    'presente': asistencia.presente,
                    'justificado': asistencia.justificado,
                    'observaciones': asistencia.observaciones,
                    'clase_horario': asistencia.clase.horario
                })
            
            return JsonResponse({
                'success': True,
                'asistencias': asistencias_data
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

# ============================================================================
# VISTAS PARA REPORTES Y RESUMENES
# ============================================================================

@method_decorator(login_required, name='dispatch')
class ResumenGeneralDocenteView(View):
    """
    Vista para obtener el resumen general del docente con datos reales
    """
    
    def get(self, request):
        # Verificar que sea docente
        if not (hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'docente')):
            return JsonResponse({'success': False, 'error': 'No tienes permisos de docente'})
        
        try:
            docente = request.user.usuario.docente
            
            # Obtener asignaturas que imparte de forma segura
            try:
                asignaturas_impartidas = AsignaturaImpartida.objects.filter(docente=docente)
                total_asignaturas = asignaturas_impartidas.count()
            except:
                total_asignaturas = 0
            
            # Calcular cursos únicos de forma segura
            try:
                cursos_unicos = set()
                for asignatura_impartida in asignaturas_impartidas:
                    clases = Clase.objects.filter(asignatura_impartida=asignatura_impartida)
                    for clase in clases:
                        if clase.curso:
                            cursos_unicos.add(clase.curso.id)
                total_cursos = len(cursos_unicos)
            except:
                total_cursos = 0
            
            # Calcular estudiantes únicos de forma segura
            try:
                estudiantes_unicos = set()
                for asignatura_impartida in asignaturas_impartidas:
                    clases = Clase.objects.filter(asignatura_impartida=asignatura_impartida)
                    asistencias = Asistencia.objects.filter(clase__in=clases)
                    for asistencia in asistencias:
                        estudiantes_unicos.add(asistencia.estudiante.pk)
                total_estudiantes = len(estudiantes_unicos)
            except:
                total_estudiantes = 0
            
            # Verificar si es profesor jefe de forma segura
            try:
                profesor_jefe = ProfesorJefe.objects.filter(docente=docente).first()
                es_profesor_jefe = profesor_jefe is not None
                curso_jefe = None
                if es_profesor_jefe and profesor_jefe.curso:
                    curso_jefe = f"{profesor_jefe.curso.nivel}°{profesor_jefe.curso.letra}"
            except:
                es_profesor_jefe = False
                curso_jefe = None
            
            # Calcular estadísticas de asistencia de forma segura
            try:
                total_asistencias = 0
                total_presentes = 0
                
                for asignatura_impartida in asignaturas_impartidas:
                    clases = Clase.objects.filter(asignatura_impartida=asignatura_impartida)
                    asistencias = Asistencia.objects.filter(clase__in=clases)
                    total_asistencias += asistencias.count()
                    total_presentes += asistencias.filter(presente=True).count()
                
                porcentaje_asistencia_general = (total_presentes / total_asistencias * 100) if total_asistencias > 0 else 0
            except:
                porcentaje_asistencia_general = 0
            
            # Calcular estadísticas de evaluaciones de forma segura
            try:
                total_evaluaciones = 0
                suma_promedios = 0
                total_estudiantes_evaluados = 0
                estudiantes_aprobados = 0
                
                for asignatura_impartida in asignaturas_impartidas:
                    evaluaciones = Evaluacion.objects.filter(asignatura_impartida=asignatura_impartida)
                    total_evaluaciones += evaluaciones.count()
                    
                    for evaluacion in evaluaciones:
                        alumno_evaluaciones = AlumnoEvaluacion.objects.filter(evaluacion=evaluacion)
                        for alumno_eval in alumno_evaluaciones:
                            if alumno_eval.nota is not None:
                                suma_promedios += alumno_eval.nota
                                total_estudiantes_evaluados += 1
                                if alumno_eval.nota >= 4.0:
                                    estudiantes_aprobados += 1
                
                promedio_general = (suma_promedios / total_estudiantes_evaluados) if total_estudiantes_evaluados > 0 else 0
                porcentaje_aprobacion = (estudiantes_aprobados / total_estudiantes_evaluados * 100) if total_estudiantes_evaluados > 0 else 0
                porcentaje_riesgo = 100 - porcentaje_aprobacion if porcentaje_aprobacion > 0 else 0
            except:
                total_evaluaciones = 0
                promedio_general = 0
                porcentaje_aprobacion = 0
                porcentaje_riesgo = 0
            
            # Identificar estudiantes en riesgo de forma segura
            try:
                estudiantes_riesgo = []
                
                for asignatura_impartida in asignaturas_impartidas:
                    clases = Clase.objects.filter(asignatura_impartida=asignatura_impartida)
                    asistencias = Asistencia.objects.filter(clase__in=clases)
                    
                    # Agrupar por estudiante
                    estudiantes_asistencia = {}
                    for asistencia in asistencias:
                        est_id = asistencia.estudiante.pk
                        if est_id not in estudiantes_asistencia:
                            estudiantes_asistencia[est_id] = {
                                'estudiante': asistencia.estudiante,
                                'total': 0,
                                'presentes': 0
                            }
                        estudiantes_asistencia[est_id]['total'] += 1
                        if asistencia.presente:
                            estudiantes_asistencia[est_id]['presentes'] += 1
                    
                    for est_id, data in estudiantes_asistencia.items():
                        if data['total'] > 0:
                            porcentaje_asist = (data['presentes'] / data['total'] * 100)
                            if porcentaje_asist < 80:
                                estudiante = data['estudiante']
                                # Obtener curso del estudiante de forma segura
                                try:
                                    curso_estudiante = "Sin curso"
                                    if hasattr(estudiante, 'curso') and estudiante.curso:
                                        curso_estudiante = f"{estudiante.curso.nivel}°{estudiante.curso.letra}"
                                    
                                    estudiantes_riesgo.append({
                                        'nombre': estudiante.usuario.get_full_name(),
                                        'curso': curso_estudiante,
                                        'asistencia': round(porcentaje_asist, 1),
                                        'motivo': 'Baja asistencia'
                                    })
                                except:
                                    continue
                
                # Limitar a 5 estudiantes en riesgo
                estudiantes_riesgo = estudiantes_riesgo[:5]
            except:
                estudiantes_riesgo = []
            
            return JsonResponse({
                'success': True,
                'docente': {
                    'nombre': docente.usuario.get_full_name(),
                    'es_profesor_jefe': es_profesor_jefe,
                    'curso_jefe': curso_jefe
                },
                'estadisticas': {
                    'total_asignaturas': total_asignaturas,
                    'total_cursos': total_cursos,
                    'total_estudiantes': total_estudiantes,
                    'total_evaluaciones': total_evaluaciones,
                    'porcentaje_asistencia_general': round(porcentaje_asistencia_general, 1),
                    'promedio_general': round(promedio_general, 2),
                    'porcentaje_aprobacion': round(porcentaje_aprobacion, 1),
                    'porcentaje_riesgo': round(porcentaje_riesgo, 1)
                },
                'evaluaciones_proximas': [],
                'evaluaciones_pendientes': [],
                'estudiantes_riesgo': estudiantes_riesgo
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error interno: {str(e)}'})


@method_decorator(login_required, name='dispatch')
class ReporteEvaluacionesAsignaturasDocenteView(View):
    """Vista para reporte de evaluaciones de las asignaturas que imparte el docente"""
    
    def get(self, request):
        # Verificar que sea docente
        if not (hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'docente')):
            return JsonResponse({'success': False, 'error': 'No tienes permisos de docente'})
        
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
                            estado_clase = "success"
                        elif promedio_asignatura >= 4.5:
                            estado = "Bueno"
                            estado_clase = "info"
                        elif promedio_asignatura >= 4.0:
                            estado = "Regular"
                            estado_clase = "warning"
                        else:
                            estado = "Deficiente"
                            estado_clase = "danger"
                    else:
                        promedio_asignatura = 0
                        nota_maxima = 0
                        nota_minima = 0
                        aprobados = 0
                        reprobados = 0
                        porcentaje_aprobacion = 0
                        estudiantes_evaluados = 0
                        estado = "Sin notas"
                        estado_clase = "secondary"
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
                    estado_clase = "secondary"
                
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
                    'estado': estado,
                    'estado_clase': estado_clase
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
            
            return JsonResponse({
                'success': True,
                'docente': docente.usuario.get_full_name(),
                'asignaturas': asignaturas_data,
                'estadisticas_generales': {
                    'total_asignaturas': len(asignaturas_data),
                    'total_evaluaciones': total_evaluaciones_general,
                    'total_notas': total_notas_general,
                    'promedio_general': round(promedio_general, 2),
                    'porcentaje_aprobacion_general': round(porcentaje_aprobacion_general, 1)
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(login_required, name='dispatch')
class ReporteEvaluacionesCursoJefeView(View):
    """Vista para reporte de evaluaciones del curso donde es profesor jefe"""
    
    def get(self, request):
        # Verificar que sea docente
        if not (hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'docente')):
            return JsonResponse({'success': False, 'error': 'No tienes permisos de docente'})
        
        try:
            docente = request.user.usuario.docente
            
            # Verificar si es profesor jefe
            profesor_jefe = ProfesorJefe.objects.filter(docente=docente).first()
            
            if not profesor_jefe or not profesor_jefe.curso:
                return JsonResponse({
                    'success': False, 
                    'error': 'No eres profesor jefe de ningún curso'
                })
            
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
                            estado_clase = "success"
                        elif promedio_asignatura >= 4.5:
                            estado = "Bueno"
                            estado_clase = "info"
                        elif promedio_asignatura >= 4.0:
                            estado = "Regular"
                            estado_clase = "warning"
                        else:
                            estado = "Deficiente"
                            estado_clase = "danger"
                    else:
                        promedio_asignatura = 0
                        nota_maxima = 0
                        nota_minima = 0
                        aprobados = 0
                        reprobados = 0
                        porcentaje_aprobacion = 0
                        estudiantes_evaluados = 0
                        estado = "Sin notas"
                        estado_clase = "secondary"
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
                    estado_clase = "secondary"
                
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
                    'estado': estado,
                    'estado_clase': estado_clase
                })
            
            # Ordenar por promedio descendente
            asignaturas_data.sort(key=lambda x: x['promedio_asignatura'], reverse=True)
            
            # Calcular estadísticas generales del curso
            if asignaturas_data:
                total_evaluaciones_curso = sum(a['total_evaluaciones'] for a in asignaturas_data)
                total_notas_curso = sum(a['total_notas'] for a in asignaturas_data)
                
                if total_notas_curso > 0:
                    porcentaje_aprobacion_curso = (total_notas_curso / total_evaluaciones_curso * 100)
                else:
                    porcentaje_aprobacion_curso = 0
                
                total_clases_curso = sum(a['total_evaluaciones'] for a in asignaturas_data)
                total_estudiantes_riesgo_curso = sum(a['estudiantes_evaluados'] for a in asignaturas_data)
            else:
                total_evaluaciones_curso = 0
                total_notas_curso = 0
                porcentaje_aprobacion_curso = 0
                total_clases_curso = 0
                total_estudiantes_riesgo_curso = 0
            
            # Obtener total de estudiantes del curso
            total_estudiantes_curso = curso.estudiantes.count()
            
            return JsonResponse({
                'success': True,
                'curso': f"{curso.nivel}°{curso.letra}",
                'curso_id': curso.id,
                'docente': docente.usuario.get_full_name(),
                'asignaturas': asignaturas_data,
                'estadisticas_generales': {
                    'total_estudiantes': total_estudiantes_curso,
                    'total_asignaturas': len(asignaturas_data),
                    'total_evaluaciones': total_evaluaciones_curso,
                    'total_notas': total_notas_curso,
                    'porcentaje_aprobacion_curso': round(porcentaje_aprobacion_curso, 1),
                    'total_estudiantes_riesgo': total_estudiantes_riesgo_curso
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(login_required, name='dispatch')
class ReporteAsistenciaAsignaturasDocenteView(View):
    """Vista para reporte de asistencia de las asignaturas que imparte el docente"""
    
    def get(self, request):
        # Verificar que sea docente
        if not (hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'docente')):
            return JsonResponse({'success': False, 'error': 'No tienes permisos de docente'})
        
        try:
            docente = request.user.usuario.docente
            
            # Obtener asignaturas que imparte el docente
            asignaturas_impartidas = AsignaturaImpartida.objects.filter(docente=docente)
            
            asignaturas_data = []
            
            for asignatura_impartida in asignaturas_impartidas:
                # Obtener clases de esta asignatura
                clases = Clase.objects.filter(asignatura_impartida=asignatura_impartida)
                
                # Obtener asistencias de todas las clases de esta asignatura
                asistencias = Asistencia.objects.filter(clase__in=clases)
                total_registros = asistencias.count()
                
                if total_registros > 0:
                    # Calcular estadísticas de asistencia
                    presentes = asistencias.filter(presente=True).count()
                    ausentes = asistencias.filter(presente=False).count()
                    porcentaje_asistencia = (presentes / total_registros * 100)
                    
                    # Estudiantes únicos con registros de asistencia
                    estudiantes_con_asistencia = asistencias.values('estudiante').distinct().count()
                    
                    # Obtener estudiantes en riesgo (asistencia < 80%)
                    estudiantes_riesgo = []
                    estudiantes_unicos = asistencias.values('estudiante').distinct()
                    
                    for est in estudiantes_unicos:
                        est_asistencias = asistencias.filter(estudiante=est['estudiante'])
                        est_total = est_asistencias.count()
                        est_presentes = est_asistencias.filter(presente=True).count()
                        
                        if est_total > 0:
                            est_porcentaje = (est_presentes / est_total * 100)
                            if est_porcentaje < 80:
                                estudiantes_riesgo.append(est['estudiante'])
                    
                    # Estado según porcentaje de asistencia
                    if porcentaje_asistencia >= 90:
                        estado = "Excelente"
                        estado_clase = "success"
                    elif porcentaje_asistencia >= 80:
                        estado = "Bueno"
                        estado_clase = "info"
                    elif porcentaje_asistencia >= 70:
                        estado = "Regular"
                        estado_clase = "warning"
                    else:
                        estado = "Deficiente"
                        estado_clase = "danger"
                else:
                    presentes = 0
                    ausentes = 0
                    porcentaje_asistencia = 0
                    estudiantes_con_asistencia = 0
                    estudiantes_riesgo = []
                    estado = "Sin registros"
                    estado_clase = "secondary"
                
                # Obtener cursos donde se imparte (para asignaturas regulares)
                cursos_str = []
                total_clases_programadas = 0
                for clase in clases:
                    if clase.curso:
                        curso_nombre = f"{clase.curso.nivel}°{clase.curso.letra}"
                        if curso_nombre not in cursos_str:
                            cursos_str.append(curso_nombre)
                    total_clases_programadas += 1
                
                asignaturas_data.append({
                    'asignatura': asignatura_impartida.asignatura.nombre,
                    'codigo': asignatura_impartida.codigo,
                    'cursos': ', '.join(cursos_str) if cursos_str else 'Electivo',
                    'total_clases_programadas': total_clases_programadas,
                    'total_registros_asistencia': total_registros,
                    'estudiantes_con_asistencia': estudiantes_con_asistencia,
                    'presentes': presentes,
                    'ausentes': ausentes,
                    'porcentaje_asistencia': round(porcentaje_asistencia, 1) if porcentaje_asistencia else 0,
                    'estudiantes_en_riesgo': len(estudiantes_riesgo),
                    'estado': estado,
                    'estado_clase': estado_clase
                })
            
            # Ordenar por porcentaje de asistencia descendente
            asignaturas_data.sort(key=lambda x: x['porcentaje_asistencia'], reverse=True)
            
            # Calcular estadísticas generales
            if asignaturas_data:
                total_registros_general = sum(a['total_registros_asistencia'] for a in asignaturas_data)
                total_presentes_general = sum(a['presentes'] for a in asignaturas_data)
                
                if total_registros_general > 0:
                    porcentaje_asistencia_general = (total_presentes_general / total_registros_general * 100)
                else:
                    porcentaje_asistencia_general = 0
                
                total_clases_general = sum(a['total_clases_programadas'] for a in asignaturas_data)
                total_estudiantes_riesgo = sum(a['estudiantes_en_riesgo'] for a in asignaturas_data)
            else:
                total_registros_general = 0
                total_clases_general = 0
                porcentaje_asistencia_general = 0
                total_estudiantes_riesgo = 0
            
            return JsonResponse({
                'success': True,
                'docente': docente.usuario.get_full_name(),
                'asignaturas': asignaturas_data,
                'estadisticas_generales': {
                    'total_asignaturas': len(asignaturas_data),
                    'total_clases_programadas': total_clases_general,
                    'total_registros_asistencia': total_registros_general,
                    'porcentaje_asistencia_general': round(porcentaje_asistencia_general, 1),
                    'total_estudiantes_riesgo': total_estudiantes_riesgo
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(login_required, name='dispatch')
class ReporteAsistenciaCursoJefeView(View):
    """Vista para reporte de asistencia del curso donde es profesor jefe"""
    
    def get(self, request):
        # Verificar que sea docente
        if not (hasattr(request.user, 'usuario') and hasattr(request.user.usuario, 'docente')):
            return JsonResponse({'success': False, 'error': 'No tienes permisos de docente'})
        
        try:
            docente = request.user.usuario.docente
            
            # Verificar si es profesor jefe
            profesor_jefe = ProfesorJefe.objects.filter(docente=docente).first()
            
            if not profesor_jefe or not profesor_jefe.curso:
                return JsonResponse({
                    'success': False, 
                    'error': 'No eres profesor jefe de ningún curso'
                })
            
            curso = profesor_jefe.curso
            
            # Obtener todas las asignaturas impartidas en el curso
            asignaturas_impartidas = AsignaturaImpartida.objects.filter(
                clases__curso=curso
            ).distinct()
            
            asignaturas_data = []
            
            for asignatura_impartida in asignaturas_impartidas:
                # Obtener asistencias de esta asignatura en el curso específico
                asistencias_curso = Asistencia.objects.filter(
                    clase__asignatura_impartida=asignatura_impartida,
                    clase__curso=curso
                )
                total_registros = asistencias_curso.count()
                
                if total_registros > 0:
                    # Calcular estadísticas de asistencia
                    presentes = asistencias_curso.filter(presente=True).count()
                    ausentes = asistencias_curso.filter(presente=False).count()
                    porcentaje_asistencia = (presentes / total_registros * 100)
                    
                    # Estudiantes del curso con registros de asistencia
                    estudiantes_con_asistencia = asistencias_curso.values('estudiante').distinct().count()
                    
                    # Obtener estudiantes en riesgo (asistencia < 80%)
                    estudiantes_riesgo = []
                    estudiantes_curso = curso.estudiantes.all()
                    
                    for estudiante in estudiantes_curso:
                        est_asistencias = asistencias_curso.filter(estudiante=estudiante)
                        est_total = est_asistencias.count()
                        est_presentes = est_asistencias.filter(presente=True).count()
                        
                        if est_total > 0:
                            est_porcentaje = (est_presentes / est_total * 100)
                            if est_porcentaje < 80:
                                estudiantes_riesgo.append(estudiante.pk)
                    
                    # Estado según porcentaje de asistencia
                    if porcentaje_asistencia >= 90:
                        estado = "Excelente"
                        estado_clase = "success"
                    elif porcentaje_asistencia >= 80:
                        estado = "Bueno"
                        estado_clase = "info"
                    elif porcentaje_asistencia >= 70:
                        estado = "Regular"
                        estado_clase = "warning"
                    else:
                        estado = "Deficiente"
                        estado_clase = "danger"
                else:
                    presentes = 0
                    ausentes = 0
                    porcentaje_asistencia = 0
                    estudiantes_con_asistencia = 0
                    estudiantes_riesgo = []
                    estado = "Sin registros"
                    estado_clase = "secondary"
                
                # Información del docente
                docente_nombre = "Sin asignar"
                if asignatura_impartida.docente:
                    docente_nombre = asignatura_impartida.docente.usuario.get_full_name()
                
                # Contar clases programadas para esta asignatura en el curso
                clases_programadas = Clase.objects.filter(
                    asignatura_impartida=asignatura_impartida,
                    curso=curso
                ).count()
                
                asignaturas_data.append({
                    'asignatura': asignatura_impartida.asignatura.nombre,
                    'codigo': asignatura_impartida.codigo,
                    'docente': docente_nombre,
                    'total_clases_programadas': clases_programadas,
                    'total_registros_asistencia': total_registros,
                    'estudiantes_con_asistencia': estudiantes_con_asistencia,
                    'presentes': presentes,
                    'ausentes': ausentes,
                    'porcentaje_asistencia': round(porcentaje_asistencia, 1) if porcentaje_asistencia else 0,
                    'estudiantes_en_riesgo': len(estudiantes_riesgo),
                    'estado': estado,
                    'estado_clase': estado_clase
                })
            
            # Ordenar por porcentaje de asistencia descendente
            asignaturas_data.sort(key=lambda x: x['porcentaje_asistencia'], reverse=True)
            
            # Calcular estadísticas generales del curso
            if asignaturas_data:
                total_registros_curso = sum(a['total_registros_asistencia'] for a in asignaturas_data)
                total_presentes_curso = sum(a['presentes'] for a in asignaturas_data)
                
                if total_registros_curso > 0:
                    porcentaje_aprobacion_curso = (total_presentes_curso / total_registros_curso * 100)
                else:
                    porcentaje_aprobacion_curso = 0
                
                total_clases_curso = sum(a['total_clases_programadas'] for a in asignaturas_data)
                total_estudiantes_riesgo_curso = sum(a['estudiantes_en_riesgo'] for a in asignaturas_data)
            else:
                total_registros_curso = 0
                total_clases_curso = 0
                porcentaje_aprobacion_curso = 0
                total_estudiantes_riesgo_curso = 0
            
            # Obtener total de estudiantes del curso
            total_estudiantes_curso = curso.estudiantes.count()
            
            return JsonResponse({
                'success': True,
                'curso': f"{curso.nivel}°{curso.letra}",
                'curso_id': curso.id,
                'docente': docente.usuario.get_full_name(),
                'asignaturas': asignaturas_data,
                'estadisticas_generales': {
                    'total_estudiantes': total_estudiantes_curso,
                    'total_asignaturas': len(asignaturas_data),
                    'total_clases_programadas': total_clases_curso,
                    'total_registros_asistencia': total_registros_curso,
                    'porcentaje_aprobacion_curso': round(porcentaje_aprobacion_curso, 1),
                    'total_estudiantes_riesgo': total_estudiantes_riesgo_curso
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

# ============================================================================
# VISTAS PARA EL SISTEMA DE NOTAS Y EVALUACIONES
# ============================================================================

@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class GenerarEvaluacionBaseView(View):
    """
    Vista para generar una evaluación base para una asignatura
    """
    
    def post(self, request, asignatura_id):
        try:
            # Verificar que el usuario sea docente
            if not hasattr(request.user.usuario, 'docente'):
                return JsonResponse({
                    'success': False,
                    'error': 'Solo los docentes pueden generar evaluaciones'
                })
            
            docente = request.user.usuario.docente
            
            # Verificar que la asignatura pertenezca al docente
            try:
                asignatura_impartida = AsignaturaImpartida.objects.get(
                    id=asignatura_id,
                    docente=docente
                )
                asignatura = asignatura_impartida.asignatura
            except AsignaturaImpartida.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Asignatura no encontrada o no tienes permisos'
                })
            
            # Obtener datos del formulario
            data = json.loads(request.body)
            nombre = data.get('nombre')
            descripcion = data.get('descripcion', '')
            ponderacion = data.get('ponderacion')
            
            # Validaciones
            if not nombre or not ponderacion:
                return JsonResponse({
                    'success': False,
                    'error': 'Nombre y ponderación son obligatorios'
                })
            
            try:
                ponderacion = float(ponderacion)
                if ponderacion <= 0 or ponderacion > 100:
                    return JsonResponse({
                        'success': False,
                        'error': 'La ponderación debe estar entre 0 y 100'
                    })
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Ponderación inválida'
                })
            
            # Crear la evaluación base
            evaluacion_base = EvaluacionBase.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                asignatura=asignatura,
                ponderacion=ponderacion
            )
            
            return JsonResponse({
                'success': True,
                'evaluacion_base': {
                    'id': evaluacion_base.id,
                    'nombre': evaluacion_base.nombre,
                    'descripcion': evaluacion_base.descripcion,
                    'ponderacion': float(evaluacion_base.ponderacion)
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class CrearEvaluacionEspecificaView(View):
    """
    Vista para crear una evaluación específica basada en una evaluación base
    """
    
    def post(self, request):
        try:
            # Verificar que el usuario sea docente
            if not hasattr(request.user.usuario, 'docente'):
                return JsonResponse({
                    'success': False,
                    'error': 'Solo los docentes pueden crear evaluaciones'
                })
            
            docente = request.user.usuario.docente
            
            # Obtener datos del formulario
            data = json.loads(request.body)
            evaluacion_base_id = data.get('evaluacion_base_id')
            clase_id = data.get('clase_id')
            fecha = data.get('fecha')
            observaciones = data.get('observaciones', '')
            
            # Validaciones
            if not evaluacion_base_id or not clase_id or not fecha:
                return JsonResponse({
                    'success': False,
                    'error': 'Evaluación base, clase y fecha son obligatorios'
                })
            
            # Verificar que la evaluación base pertenezca a una asignatura del docente
            try:
                evaluacion_base = EvaluacionBase.objects.get(
                    id=evaluacion_base_id,
                    asignatura__asignaturaimpartida__docente=docente
                )
            except EvaluacionBase.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Evaluación base no encontrada o no tienes permisos'
                })
            
            # Verificar que la clase pertenezca al docente
            try:
                clase = Clase.objects.get(
                    id=clase_id,
                    asignatura_impartida__docente=docente
                )
            except Clase.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Clase no encontrada o no tienes permisos'
                })
            
            # Validar lógica de bloques pares/impares
            horario_str = str(clase.horario)
            import re
            match = re.match(r'^(\d+)', horario_str)
            if match:
                numero_bloque = int(match.group(1))
                es_bloque_par = numero_bloque % 2 == 0
                
                # Para asignaturas regulares, solo permitir bloques pares (2-4, 6-8, etc.)
                # Para asignaturas especiales, solo permitir bloques impares (1-2, 3-4, etc.)
                # Por ahora, permitimos ambos tipos pero con validación
                if es_bloque_par:
                    # Es un bloque par (2-4, 6-8, etc.)
                    pass  # Permitir
                else:
                    # Es un bloque impar (1-2, 3-4, etc.)
                    pass  # Permitir
                    
                # Aquí se puede agregar lógica específica según el tipo de asignatura
                # Por ejemplo, verificar si la asignatura es especial o regular
            
            # Convertir fecha
            try:
                fecha_evaluacion = datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Formato de fecha inválido'
                })
            
            # Verificar que no exista ya una evaluación para esta evaluación base en esta clase
            evaluacion_existente = Evaluacion.objects.filter(
                evaluacion_base=evaluacion_base,
                clase=clase
            ).first()
            
            if evaluacion_existente:
                return JsonResponse({
                    'success': False,
                    'error': f'Ya existe una evaluación "{evaluacion_base.nombre}" para esta clase'
                })
            
            # Crear la evaluación específica
            evaluacion = Evaluacion.objects.create(
                evaluacion_base=evaluacion_base,
                clase=clase,
                fecha=fecha_evaluacion,
                observaciones=observaciones
            )
            
            return JsonResponse({
                'success': True,
                'evaluacion': {
                    'id': evaluacion.id,
                    'nombre': evaluacion.evaluacion_base.nombre,
                    'fecha': evaluacion.fecha.strftime('%Y-%m-%d'),
                    'ponderacion': float(evaluacion.evaluacion_base.ponderacion),
                    'observaciones': evaluacion.observaciones,
                    'clase': f"{clase.fecha} - {clase.horario} - {clase.sala}",
                    'curso': str(clase.curso) if clase.curso else "Electivo"
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class CrearEvaluacionesEstudiantesView(View):
    """
    Vista para crear evaluaciones para todos los estudiantes de una evaluación específica
    """
    
    def post(self, request, evaluacion_id):
        try:
            # Verificar que el usuario sea docente
            if not hasattr(request.user.usuario, 'docente'):
                return JsonResponse({
                    'success': False,
                    'error': 'Solo los docentes pueden crear evaluaciones de estudiantes'
                })
            
            docente = request.user.usuario.docente
            
            # Verificar que la evaluación pertenezca al docente
            try:
                evaluacion = Evaluacion.objects.get(
                    id=evaluacion_id,
                    clase__asignatura_impartida__docente=docente
                )
            except Evaluacion.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Evaluación no encontrada o no tienes permisos'
                })
            
            # Obtener estudiantes inscritos en la asignatura
            estudiantes = Estudiante.objects.filter(
                asignaturas_inscritas__asignatura_impartida=evaluacion.clase.asignatura_impartida,
                curso=evaluacion.clase.curso
            ).select_related('usuario')
            
            if not estudiantes.exists():
                return JsonResponse({
                    'success': False,
                    'error': 'No hay estudiantes inscritos en esta asignatura'
                })
            
            # Crear evaluaciones para cada estudiante
            evaluaciones_creadas = []
            for estudiante in estudiantes:
                # Verificar si ya existe una evaluación para este estudiante
                alumno_evaluacion, created = AlumnoEvaluacion.objects.get_or_create(
                    estudiante=estudiante,
                    evaluacion=evaluacion,
                    defaults={
                        'nota': 0.0,  # Nota inicial en 0
                        'observaciones': 'Evaluación creada automáticamente'
                    }
                )
                
                if created:
                    evaluaciones_creadas.append({
                        'id': alumno_evaluacion.id,
                        'estudiante_nombre': f"{estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}",
                        'nota': float(alumno_evaluacion.nota),
                        'observaciones': alumno_evaluacion.observaciones
                    })
            
            return JsonResponse({
                'success': True,
                'evaluaciones_creadas': evaluaciones_creadas,
                'total_estudiantes': estudiantes.count(),
                'nuevas_evaluaciones': len(evaluaciones_creadas)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


@method_decorator(login_required, name='dispatch')
class ObtenerEvaluacionesAsignaturaView(View):
    """
    Vista para obtener las evaluaciones de una asignatura
    """
    
    def get(self, request, asignatura_id):
        try:
            # Verificar que el usuario sea docente
            if not hasattr(request.user.usuario, 'docente'):
                return JsonResponse({
                    'success': False,
                    'error': 'Solo los docentes pueden ver evaluaciones'
                })
        
            docente = request.user.usuario.docente
            
            # Verificar que la asignatura pertenezca al docente
            try:
                asignatura_impartida = AsignaturaImpartida.objects.get(
                    id=asignatura_id,
                    docente=docente
                )
            except AsignaturaImpartida.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Asignatura no encontrada o no tienes permisos'
                })
            
            # Obtener evaluaciones base de la asignatura
            evaluaciones_base = EvaluacionBase.objects.filter(
                asignatura=asignatura_impartida.asignatura
            ).values('id', 'nombre', 'descripcion', 'ponderacion')
            
            # Obtener evaluaciones específicas
            evaluaciones = Evaluacion.objects.filter(
                clase__asignatura_impartida=asignatura_impartida
            ).select_related('evaluacion_base', 'clase__curso').values(
                'id', 'evaluacion_base__nombre', 'evaluacion_base__ponderacion',
                'fecha', 'observaciones', 'clase__curso__nivel', 'clase__curso__letra'
            )
            
            return JsonResponse({
                'success': True,
                'evaluaciones_base': list(evaluaciones_base),
                'evaluaciones': list(evaluaciones)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


@method_decorator(login_required, name='dispatch')
class ObtenerNotasEvaluacionView(View):
    """
    Vista para obtener las notas de una evaluación específica
    """
    
    def get(self, request, evaluacion_id):
        try:
            # Verificar que el usuario sea docente
            if not hasattr(request.user.usuario, 'docente'):
                return JsonResponse({
                    'success': False,
                    'error': 'Solo los docentes pueden ver notas'
                })
            
            docente = request.user.usuario.docente
            
            # Verificar que la evaluación pertenezca al docente
            try:
                evaluacion = Evaluacion.objects.get(
                    id=evaluacion_id,
                    clase__asignatura_impartida__docente=docente
                )
            except Evaluacion.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Evaluación no encontrada o no tienes permisos'
                })
            
            # Obtener notas de la evaluación
            notas = AlumnoEvaluacion.objects.filter(
                evaluacion=evaluacion
            ).select_related('estudiante__usuario').values(
                'id', 'nota', 'observaciones',
                'estudiante__usuario__nombre',
                'estudiante__usuario__apellido_paterno'
            )
            
            # Formatear datos
            notas_formateadas = []
            for nota in notas:
                notas_formateadas.append({
                    'id': nota['id'],
                    'estudiante_nombre': f"{nota['estudiante__usuario__nombre']} {nota['estudiante__usuario__apellido_paterno']}",
                    'nota': float(nota['nota']),
                    'observaciones': nota['observaciones'],
                    'fecha': evaluacion.fecha.strftime('%Y-%m-%d')
                })
            
            return JsonResponse({
                'success': True,
                'notas': notas_formateadas
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ActualizarNotaView(View):
    """
    Vista para actualizar una nota específica
    """
    
    def put(self, request, nota_id):
        try:
            # Verificar que el usuario sea docente
            if not hasattr(request.user.usuario, 'docente'):
                return JsonResponse({
                    'success': False, 
                    'error': 'Solo los docentes pueden actualizar notas'
                })
            
            docente = request.user.usuario.docente
            
            # Verificar que la nota pertenezca a una evaluación del docente
            try:
                nota = AlumnoEvaluacion.objects.get(
                    id=nota_id,
                    evaluacion__clase__asignatura_impartida__docente=docente
                )
            except AlumnoEvaluacion.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Nota no encontrada o no tienes permisos'
                })
            
            # Obtener datos del formulario
            data = json.loads(request.body)
            nueva_nota = data.get('nota')
            observaciones = data.get('observaciones', nota.observaciones)
            
            # Validaciones
            if nueva_nota is None:
                return JsonResponse({
                    'success': False,
                    'error': 'La nota es obligatoria'
                })
                
            try:
                nueva_nota = float(nueva_nota)
                if nueva_nota < 1.0 or nueva_nota > 7.0:
                    return JsonResponse({
                        'success': False,
                        'error': 'La nota debe estar entre 1.0 y 7.0'
                    })
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Nota inválida'
                })
            
            # Actualizar la nota
            nota.nota = nueva_nota
            nota.observaciones = observaciones
            nota.save()
            
            return JsonResponse({
                'success': True,
                'nota': {
                    'id': nota.id,
                    'nota': float(nota.nota),
                    'observaciones': nota.observaciones
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class EliminarNotaView(View):
    """
    Vista para eliminar una nota específica
    """
    
    def delete(self, request, nota_id):
        try:
            # Verificar que el usuario sea docente
            if not hasattr(request.user.usuario, 'docente'):
                return JsonResponse({
                    'success': False,
                    'error': 'Solo los docentes pueden eliminar notas'
                })
            
            docente = request.user.usuario.docente
            
            # Verificar que la nota pertenezca a una evaluación del docente
            try:
                nota = AlumnoEvaluacion.objects.get(
                    id=nota_id,
                    evaluacion__clase__asignatura_impartida__docente=docente
                )
            except AlumnoEvaluacion.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Nota no encontrada o no tienes permisos'
                })
            
            # Eliminar la nota
            nota.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Nota eliminada correctamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@method_decorator(login_required, name='dispatch')
class ObtenerClasesDocenteView(View):
    """
    Vista para obtener las clases disponibles del docente para una asignatura específica
    """
    
    def get(self, request, asignatura_id):
        try:
            # Verificar que el usuario sea docente
            if not hasattr(request.user.usuario, 'docente'):
                return JsonResponse({
                    'success': False,
                    'error': 'Solo los docentes pueden ver clases'
                })
        
            docente = request.user.usuario.docente
            
            # Verificar que la asignatura pertenezca al docente
            try:
                asignatura_impartida = AsignaturaImpartida.objects.get(
                    id=asignatura_id,
                    docente=docente
                )
            except AsignaturaImpartida.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Asignatura no encontrada o no tienes permisos'
                })
            
            # Obtener clases de la asignatura
            clases = Clase.objects.filter(
                asignatura_impartida=asignatura_impartida
            ).select_related('curso').order_by('fecha', 'horario')
            
            clases_data = []
            for clase in clases:
                # Determinar si es bloque par o impar
                horario_str = str(clase.horario)
                es_bloque_par = False
                
                # Extraer el primer número del horario (ej: "1-2" -> 1, "3-4" -> 3)
                import re
                match = re.match(r'^(\d+)', horario_str)
                if match:
                    numero_bloque = int(match.group(1))
                    es_bloque_par = numero_bloque % 2 == 0
                
                clases_data.append({
                    'id': clase.id,
                    'dia': clase.fecha,
                    'horario': clase.horario,
                    'sala': clase.sala,
                    'curso': str(clase.curso) if clase.curso else "Electivo",
                    'es_bloque_par': es_bloque_par,
                    'numero_bloque': int(match.group(1)) if match else 0,
                    'descripcion': f"{clase.fecha} - {clase.horario} - {clase.sala} ({str(clase.curso) if clase.curso else 'Electivo'})"
                })
            
            return JsonResponse({
                'success': True,
                'clases': clases_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
