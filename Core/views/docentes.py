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
        clases_canceladas = get_clases_canceladas_docente(docente.pk)
        
        # Obtener comunicaciones del docente
        datos_comunicaciones = get_comunicaciones_docente(docente)
        
        # Obtener todos los cursos para filtros
        cursos = Curso.objects.all().order_by('nivel', 'letra')
        
        context = {
            'cursos_profesor_jefe': cursos_profesor_jefe,
            'asignaturas': asignaturas,
            'evaluaciones_docente': evaluaciones_docente,
            'estadisticas_docente': estadisticas_docente,
            'estadisticas_asistencia': estadisticas_asistencia,
            'eventos_calendario': eventos_calendario,
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
            
            # Preparar los horarios
            horarios = []
            for clase in clases:
                horarios.append({
                    'dia': clase.fecha,
                    'bloque': clase.horario,
                    'sala': clase.get_sala_display() if hasattr(clase, 'get_sala_display') else clase.sala,
                    'curso': str(clase.curso) if clase.curso else 'Electivo'
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
class CrearEventoCalendarioView(View):
    """
    Vista para crear eventos desde el formulario del calendario general
    """
    
    def post(self, request):
        try:
            # Verificar que el usuario sea docente
            if not hasattr(request.user.usuario, 'docente'):
                return JsonResponse({
                    'success': False,
                    'error': 'Solo los docentes pueden crear eventos'
                })
            
            docente = request.user.usuario.docente
            
            # Obtener datos del formulario
            tipo = request.POST.get('tipo')
            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion', '')
            fecha_str = request.POST.get('fecha')
            bloque_horario = request.POST.get('bloque_horario')
            asignatura_id = request.POST.get('asignatura_id')
            ubicacion = request.POST.get('ubicacion', '')
            materiales = request.POST.get('materiales', '')
            instrucciones = request.POST.get('instrucciones', '')
            ponderacion = request.POST.get('ponderacion')
            tipo_evaluacion = request.POST.get('tipo_evaluacion', '')
            
            # Validaciones básicas
            if not tipo or not titulo or not fecha_str:
                return JsonResponse({
                    'success': False,
                    'error': 'Faltan campos obligatorios'
                })
            
            # Validaciones para evaluaciones
            if tipo == 'EVALUACION':
                if not asignatura_id or not bloque_horario:
                    return JsonResponse({
                        'success': False,
                        'error': 'Para evaluaciones, la asignatura y bloque son obligatorios'
                    })
            
            # Convertir fecha
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Formato de fecha inválido'
                })
            
            # Calcular hora basada en el bloque
            hora_evento = self.calcular_hora_desde_bloque(bloque_horario)
            
            # Crear el evento según el tipo
            if tipo in ['EVALUACION', 'TAREA', 'MATERIAL', 'ENTREGA', 'CANCELAR_CLASE'] and asignatura_id:
                # Crear en CalendarioClase
                try:
                    # Buscar AsignaturaImpartida que pertenezca al docente
                    asignatura_impartida = AsignaturaImpartida.objects.get(
                        id=asignatura_id,
                        docente=docente
                    )
                    asignatura = asignatura_impartida.asignatura
                    
                    evento = CalendarioClase.objects.create(
                        nombre_actividad=titulo,
                        asignatura=asignatura,
                        descripcion=descripcion,
                        materiales=materiales if materiales else None,
                        fecha=fecha,
                        hora=hora_evento
                    )
                    
                    # Si es evaluación, crear también en EvaluacionBase
                    if tipo == 'EVALUACION' and ponderacion:
                        try:
                            EvaluacionBase.objects.create(
                                nombre=titulo,
                                descripcion=descripcion,
                                asignatura=asignatura,  # Usar asignatura, no asignatura_impartida
                                ponderacion=float(ponderacion)
                            )
                        except ValueError:
                            pass  # Si no se puede crear la evaluación, continuamos
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Evento "{titulo}" creado exitosamente',
                        'evento_id': evento.id
                    })
                    
                except AsignaturaImpartida.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Asignatura no encontrada o no autorizada para este docente'
                    })
            else:
                # Crear en CalendarioColegio para eventos generales
                evento = CalendarioColegio.objects.create(
                    nombre_actividad=titulo,
                    descripcion=descripcion,
                    fecha=fecha,
                    hora=hora_evento,
                    encargado=f"{docente.usuario.nombre} {docente.usuario.apellido_paterno}",
                    ubicacion=ubicacion or 'Por definir'
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Evento "{titulo}" creado exitosamente',
                    'evento_id': evento.id
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al crear evento: {str(e)}'
            })
    
    def calcular_hora_desde_bloque(self, bloque_horario):
        """
        Convierte el bloque horario a una hora específica
        """
        if not bloque_horario:
            return time(8, 0)  # Hora por defecto
        
        # Mapeo de bloques a horas
        mapeo_bloques = {
            '1-2': time(8, 0),   # 08:00 - 09:30
            '3-4': time(9, 45),  # 09:45 - 11:15
            '5-6': time(11, 30), # 11:30 - 13:00
            '7-8': time(13, 45), # 13:45 - 15:15
            '9': time(15, 15),   # 15:15 - 16:00
            '1': time(8, 0),
            '2': time(8, 45),
            '3': time(9, 45),
            '4': time(10, 30),
            '5': time(11, 30),
            '6': time(12, 15),
            '7': time(13, 45),
            '8': time(14, 30),
        }
        
        return mapeo_bloques.get(bloque_horario, time(8, 0))


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class EditarEventoCalendarioView(View):
    """
    Vista para editar eventos existentes
    """
    
    def get(self, request, evento_id):
        try:
            # Verificar que el usuario sea docente
            if not hasattr(request.user.usuario, 'docente'):
                return JsonResponse({'success': False, 'error': 'No autorizado'})
            
            docente = request.user.usuario.docente
            
            # Buscar el evento - puede ser CalendarioClase o CalendarioColegio
            evento_clase = CalendarioClase.objects.filter(id=evento_id).first()
            evento_colegio = CalendarioColegio.objects.filter(id=evento_id).first()
            
            if evento_clase:
                # Verificar que la asignatura pertenezca al docente
                asignatura_docente = AsignaturaImpartida.objects.filter(
                    asignatura=evento_clase.asignatura,
                    docente=docente
                ).exists()
                
                if not asignatura_docente:
                    return JsonResponse({'success': False, 'error': 'No autorizado para editar este evento'})
                
                return JsonResponse({
                    'success': True,
                    'evento': {
                        'id': evento_clase.id,
                        'tipo': 'EVALUACION',  # Asumimos que es evaluación por defecto
                        'titulo': evento_clase.nombre_actividad,
                        'descripcion': evento_clase.descripcion or '',
                        'fecha': evento_clase.fecha.strftime('%Y-%m-%d'),
                        'hora': evento_clase.hora.strftime('%H:%M') if evento_clase.hora else '08:00',
                        'asignatura_id': AsignaturaImpartida.objects.filter(
                            asignatura=evento_clase.asignatura,
                            docente=docente
                        ).first().id,
                        'materiales': evento_clase.materiales or '',
                        'ubicacion': '',
                        'event_type': 'clase'
                    }
                })
            
            elif evento_colegio:
                # Verificar que el docente sea el encargado
                nombre_completo = f"{docente.usuario.nombre} {docente.usuario.apellido_paterno}"
                if nombre_completo.lower() not in evento_colegio.encargado.lower():
                    return JsonResponse({'success': False, 'error': 'No autorizado para editar este evento'})
                
                return JsonResponse({
                    'success': True,
                    'evento': {
                        'id': evento_colegio.id,
                        'tipo': 'REUNION',  # Asumimos reunión por defecto
                        'titulo': evento_colegio.nombre_actividad,
                        'descripcion': evento_colegio.descripcion or '',
                        'fecha': evento_colegio.fecha.strftime('%Y-%m-%d'),
                        'hora': evento_colegio.hora.strftime('%H:%M') if evento_colegio.hora else '08:00',
                        'asignatura_id': '',
                        'materiales': '',
                        'ubicacion': evento_colegio.ubicacion or '',
                        'event_type': 'colegio'
                    }
                })
            
            else:
                return JsonResponse({'success': False, 'error': 'Evento no encontrado'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    def post(self, request, evento_id):
        try:
            # Verificar que el usuario sea docente
            if not hasattr(request.user.usuario, 'docente'):
                return JsonResponse({'success': False, 'error': 'No autorizado'})
            
            docente = request.user.usuario.docente
            
            # Obtener datos del formulario
            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion', '')
            fecha_str = request.POST.get('fecha')
            materiales = request.POST.get('materiales', '')
            ubicacion = request.POST.get('ubicacion', '')
            event_type = request.POST.get('event_type')
            
            if not titulo or not fecha_str:
                return JsonResponse({'success': False, 'error': 'Faltan campos obligatorios'})
            
            # Convertir fecha
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Formato de fecha inválido'})
            
            # Editar según el tipo de evento
            if event_type == 'clase':
                evento = CalendarioClase.objects.filter(id=evento_id).first()
                if not evento:
                    return JsonResponse({'success': False, 'error': 'Evento no encontrado'})
                
                # Verificar autorización
                asignatura_docente = AsignaturaImpartida.objects.filter(
                    asignatura=evento.asignatura,
                    docente=docente
                ).exists()
                
                if not asignatura_docente:
                    return JsonResponse({'success': False, 'error': 'No autorizado'})
                
                # Actualizar evento
                evento.nombre_actividad = titulo
                evento.descripcion = descripcion
                evento.fecha = fecha
                evento.materiales = materiales
                evento.save()
                
            elif event_type == 'colegio':
                evento = CalendarioColegio.objects.filter(id=evento_id).first()
                if not evento:
                    return JsonResponse({'success': False, 'error': 'Evento no encontrado'})
                
                # Verificar autorización
                nombre_completo = f"{docente.usuario.nombre} {docente.usuario.apellido_paterno}"
                if nombre_completo.lower() not in evento.encargado.lower():
                    return JsonResponse({'success': False, 'error': 'No autorizado'})
                
                # Actualizar evento
                evento.nombre_actividad = titulo
                evento.descripcion = descripcion
                evento.fecha = fecha
                evento.ubicacion = ubicacion
                evento.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Evento "{titulo}" actualizado exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class EliminarEventoCalendarioView(View):
    """
    Vista para eliminar eventos
    """
    
    def post(self, request, evento_id):
        try:
            # Verificar que el usuario sea docente
            if not hasattr(request.user.usuario, 'docente'):
                return JsonResponse({'success': False, 'error': 'No autorizado'})
            
            docente = request.user.usuario.docente
            event_type = request.POST.get('event_type')
            
            if event_type == 'clase':
                evento = CalendarioClase.objects.filter(id=evento_id).first()
                if not evento:
                    return JsonResponse({'success': False, 'error': 'Evento no encontrado'})
                
                # Verificar autorización
                asignatura_docente = AsignaturaImpartida.objects.filter(
                    asignatura=evento.asignatura,
                    docente=docente
                ).exists()
                
                if not asignatura_docente:
                    return JsonResponse({'success': False, 'error': 'No autorizado'})
                
                titulo = evento.nombre_actividad
                evento.delete()
                
            elif event_type == 'colegio':
                evento = CalendarioColegio.objects.filter(id=evento_id).first()
                if not evento:
                    return JsonResponse({'success': False, 'error': 'Evento no encontrado'})
                
                # Verificar autorización
                nombre_completo = f"{docente.usuario.nombre} {docente.usuario.apellido_paterno}"
                if nombre_completo.lower() not in evento.encargado.lower():
                    return JsonResponse({'success': False, 'error': 'No autorizado'})
                
                titulo = evento.nombre_actividad
                evento.delete()
            
            else:
                return JsonResponse({'success': False, 'error': 'Tipo de evento no válido'})
            
            return JsonResponse({
                'success': True,
                'message': f'Evento "{titulo}" eliminado exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

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
                    'promedio_general_curso': round(promedio_general_curso, 2),
                    'porcentaje_aprobacion_curso': round(porcentaje_aprobacion_curso, 1)
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
                    porcentaje_asistencia_curso = (total_presentes_curso / total_registros_curso * 100)
                else:
                    porcentaje_asistencia_curso = 0
                
                total_clases_curso = sum(a['total_clases_programadas'] for a in asignaturas_data)
                total_estudiantes_riesgo_curso = sum(a['estudiantes_en_riesgo'] for a in asignaturas_data)
            else:
                total_registros_curso = 0
                total_clases_curso = 0
                porcentaje_asistencia_curso = 0
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
                    'porcentaje_asistencia_curso': round(porcentaje_asistencia_curso, 1),
                    'total_estudiantes_riesgo': total_estudiantes_riesgo_curso
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
class ResumenGeneralDocenteView(View):
    """Vista para obtener el resumen general del docente con datos reales"""
    
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

