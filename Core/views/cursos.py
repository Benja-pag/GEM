from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from Core.models import (
    Usuario, Administrativo, Docente, Estudiante, Asistencia, 
    CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, 
    Asignatura, AsignaturaImpartida, Curso, ProfesorJefe, 
    Evaluacion, AlumnoEvaluacion, EvaluacionBase, ClaseCancelada, 
    Comunicacion, ForoAsignatura, MensajeForoAsignatura
)
from django.db.models import Count, Avg, Max, Min, Q
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
from Core.servicios.repos.cursos import get_curso, get_estudiantes_por_curso
from Core.servicios.alumnos.helpers import get_promedio_estudiante, get_asistencia_estudiante
from django.core.exceptions import PermissionDenied
import json
from statistics import mean
from datetime import date, timedelta, datetime, time
from decimal import Decimal
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
from django.conf import settings
import time
from collections import defaultdict

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
        
        # Obtener comunicaciones relacionadas con la asignatura
        # Filtramos por el código de la asignatura en el asunto
        cursos_asignatura = Curso.objects.filter(clases__asignatura_impartida=asignaturas.first()).distinct()
        comunicaciones = Comunicacion.objects.filter(
            Q(autor=request.user) &
            (Q(asunto__startswith=f'[{asignaturas.first().codigo}]') | 
             Q(destinatarios_cursos__in=cursos_asignatura))
        ).select_related('autor').prefetch_related(
            'leido_por', 
            'destinatarios_usuarios',
            'destinatarios_cursos'
        ).order_by('-fecha_envio').distinct()
        
        # Calcular estadísticas de comunicaciones
        total_comunicaciones = comunicaciones.count()
        total_lecturas = sum(com.leido_por.count() for com in comunicaciones)
        total_destinatarios = sum(
            com.destinatarios_usuarios.filter(usuario__estudiante__isnull=False).count() + 
            sum(curso.estudiantes.count() for curso in com.destinatarios_cursos.all())
            for com in comunicaciones
        )
        
        # Calcular tasa de lectura
        tasa_lectura = (total_lecturas / total_destinatarios * 100) if total_destinatarios > 0 else 0
        
        # Formatear comunicaciones para la vista
        comunicaciones_formateadas = []
        for com in comunicaciones:
            # Obtener los cursos destinatarios
            cursos_dest = [f"{curso.nivel}°{curso.letra}" for curso in com.destinatarios_cursos.all()]
            cursos_str = ", ".join(cursos_dest) if cursos_dest else "Sin cursos asignados"
            
            comunicaciones_formateadas.append({
                'id': com.id,  # Agregamos el ID para poder eliminar
                'asunto': com.asunto,
                'descripcion': com.contenido[:100] + '...' if len(com.contenido) > 100 else com.contenido,
                'fecha': com.fecha_envio,
                'destinatarios': [f"Asignatura {asignatura.codigo} - {cursos_str}"],
                'estado': 'Enviada',
                'total_lecturas': com.leido_por.count()
            })
        
        context = {
            'curso': curso,
            'estudiantes': estudiantes,
            'asignaturas': asignaturas,
            'profesor_jefe': profesor_jefe,
            'ranking_estudiantes': ranking_estudiantes,
            'asistencia_estudiantes': asistencia_estudiantes,
            'comunicaciones_curso': comunicaciones_formateadas,
            'estadisticas_comunicaciones': {
                'total_enviadas': total_comunicaciones,
                'tasa_lectura': round(tasa_lectura, 1),
                'total_lecturas': total_lecturas
            }
        }
        return render(request, 'teacher/curso_detalle.html', context)

def get_estadisticas_asignatura(asignatura_id):
    """
    Calcula las estadísticas generales de una asignatura
    """
    from django.db.models import Avg, Count
    from Core.models import Evaluacion, AlumnoEvaluacion, Asistencia

    # Obtener evaluaciones
    evaluaciones = Evaluacion.objects.filter(clase__asignatura_impartida_id=asignatura_id)
    total_evaluaciones = evaluaciones.count()
    
    # Calcular promedio general
    notas = AlumnoEvaluacion.objects.filter(evaluacion__in=evaluaciones)
    promedio_general = notas.aggregate(promedio=Avg('nota'))['promedio'] or 0.0
    
    # Calcular asistencia
    asistencias = Asistencia.objects.filter(clase__asignatura_impartida_id=asignatura_id)
    total_asistencias = asistencias.count()
    presentes = asistencias.filter(presente=True).count()
    porcentaje_asistencia = (presentes / total_asistencias * 100) if total_asistencias > 0 else 0
    
    # Calcular evaluaciones calificadas
    evaluaciones_calificadas = evaluaciones.filter(resultados__isnull=False).distinct().count()
    porcentaje_avance = (evaluaciones_calificadas / total_evaluaciones * 100) if total_evaluaciones > 0 else 0

    return {
        'promedio_general': round(promedio_general, 1),
        'porcentaje_asistencia': round(porcentaje_asistencia, 1),
        'porcentaje_avance': round(porcentaje_avance, 1),
        'total_evaluaciones': total_evaluaciones,
        'evaluaciones_calificadas': evaluaciones_calificadas
    }

def get_proximas_actividades(asignatura_id):
    """
    Obtiene las próximas actividades (evaluaciones y eventos) de una asignatura
    para los próximos 7 días
    """
    from datetime import date, timedelta
    from Core.models import Evaluacion, CalendarioClase, AsignaturaImpartida

    hoy = date.today()
    proxima_semana = hoy + timedelta(days=7)

    # Obtener la asignatura impartida
    asignatura_impartida = AsignaturaImpartida.objects.get(id=asignatura_id)
    
    # Obtener próximas evaluaciones
    evaluaciones = Evaluacion.objects.filter(
        clase__asignatura_impartida_id=asignatura_id,
        fecha__gte=hoy,
        fecha__lte=proxima_semana
    ).select_related('evaluacion_base', 'clase__asignatura_impartida__asignatura').order_by('fecha')
    
    # Obtener próximos eventos del calendario
    eventos = CalendarioClase.objects.filter(
        asignatura=asignatura_impartida.asignatura,
        fecha__gte=hoy,
        fecha__lte=proxima_semana
    ).order_by('fecha')
    
    actividades = []
    
    for evaluacion in evaluaciones:
        actividades.append({
            'tipo': 'Evaluación',
            'titulo': evaluacion.evaluacion_base.nombre,
            'descripcion': evaluacion.evaluacion_base.descripcion,
            'fecha': evaluacion.fecha,
            'dias_restantes': (evaluacion.fecha - hoy).days,
            'asignatura': evaluacion.clase.asignatura_impartida.asignatura.nombre
        })
    
    for evento in eventos:
        actividades.append({
            'tipo': 'Evento',
            'titulo': evento.nombre_actividad,
            'descripcion': evento.descripcion,
            'fecha': evento.fecha,
            'dias_restantes': (evento.fecha - hoy).days,
            'asignatura': evento.asignatura.nombre
        })
    
    return sorted(actividades, key=lambda x: x['fecha'])

@method_decorator(login_required, name='dispatch')
class AsignaturaDetalleView(View):
    def get(self, request, asignatura_id):
        asignatura = get_object_or_404(AsignaturaImpartida, id=asignatura_id)
        
        # Obtener estudiantes inscritos
        estudiantes = Estudiante.objects.filter(
            asignaturas_inscritas__asignatura_impartida=asignatura,
            asignaturas_inscritas__validada=True
        ).select_related('usuario', 'curso').distinct()
        
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
        
        # Obtener clases de la asignatura y agrupar por día y bloques consecutivos
        clases = Clase.objects.filter(
            asignatura_impartida=asignatura
        ).order_by('fecha', 'horario')
        
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
        clases_formateadas = []
        for dia, bloques in horarios_agrupados.items():
            for bloque in bloques:
                clases_formateadas.append({
                    'fecha': dia,
                    'horario': f"{bloque['hora_inicio']} - {bloque['hora_fin']}",
                    'sala': bloque['sala'],
                    'curso': bloque['curso']
                })
        
        # Obtener estadísticas
        estadisticas = get_estadisticas_asignatura(asignatura_id)
        
        # Obtener próximas actividades
        proximas_actividades = get_proximas_actividades(asignatura_id)

        # Obtener comunicaciones relacionadas con la asignatura
        # Filtramos por el código de la asignatura en el asunto
        cursos_asignatura = Curso.objects.filter(clases__asignatura_impartida=asignatura).distinct()
        comunicaciones = Comunicacion.objects.filter(
            Q(autor=request.user) &
            (Q(asunto__startswith=f'[{asignatura.codigo}]') | 
             Q(destinatarios_cursos__in=cursos_asignatura))
        ).select_related('autor').prefetch_related(
            'leido_por', 
            'destinatarios_usuarios',
            'destinatarios_cursos'
        ).order_by('-fecha_envio').distinct()

        # Calcular estadísticas de comunicaciones
        total_comunicaciones = comunicaciones.count()
        total_lecturas = sum(com.leido_por.count() for com in comunicaciones)
        total_destinatarios = sum(
            com.destinatarios_usuarios.filter(usuario__estudiante__isnull=False).count() + 
            sum(curso.estudiantes.count() for curso in com.destinatarios_cursos.all())
            for com in comunicaciones
        )
        
        # Calcular tasa de lectura
        tasa_lectura = (total_lecturas / total_destinatarios * 100) if total_destinatarios > 0 else 0
        
        # Formatear comunicaciones para la vista
        comunicaciones_formateadas = []
        for com in comunicaciones:
            # Obtener los cursos destinatarios
            cursos_dest = [f"{curso.nivel}°{curso.letra}" for curso in com.destinatarios_cursos.all()]
            cursos_str = ", ".join(cursos_dest) if cursos_dest else "Sin cursos asignados"
            
            comunicaciones_formateadas.append({
                'id': com.id,  # Agregamos el ID para poder eliminar
                'asunto': com.asunto,
                'descripcion': com.contenido[:100] + '...' if len(com.contenido) > 100 else com.contenido,
                'fecha': com.fecha_envio,
                'destinatarios': [f"Asignatura {asignatura.codigo} - {cursos_str}"],
                'estado': 'Enviada',
                'total_lecturas': com.leido_por.count()
            })
        
        # Obtener los últimos temas del foro
        temas_foro = ForoAsignatura.objects.filter(
            asignatura=asignatura
        ).select_related(
            'autor'
        ).prefetch_related(
            'mensajes',
            'mensajes__autor'
        ).order_by('-es_anuncio', '-fecha')[:5]

        # Obtener estadísticas detalladas de asistencia
        asistencias = Asistencia.objects.filter(
            clase__asignatura_impartida=asignatura
        ).select_related(
            'estudiante',
            'estudiante__usuario',
            'clase'
        )

        # Estadísticas generales
        total_clases = Clase.objects.filter(asignatura_impartida=asignatura).count()
        total_registros = asistencias.count()
        presentes = asistencias.filter(presente=True).count()
        ausentes = asistencias.filter(presente=False).count()
        justificados = asistencias.filter(justificado=True).count()
        porcentaje_asistencia = (presentes / total_registros * 100) if total_registros > 0 else 0

        # Estadísticas por estudiante
        estudiantes_asistencia = {}
        for asistencia in asistencias:
            est_id = asistencia.estudiante.pk
            if est_id not in estudiantes_asistencia:
                estudiantes_asistencia[est_id] = {
                    'estudiante': asistencia.estudiante,
                    'nombre': f"{asistencia.estudiante.usuario.nombre} {asistencia.estudiante.usuario.apellido_paterno}",
                    'total': 0,
                    'presentes': 0,
                    'ausentes': 0,
                    'justificados': 0
                }
            estudiantes_asistencia[est_id]['total'] += 1
            if asistencia.presente:
                estudiantes_asistencia[est_id]['presentes'] += 1
            else:
                estudiantes_asistencia[est_id]['ausentes'] += 1
            if asistencia.justificado:
                estudiantes_asistencia[est_id]['justificados'] += 1

        # Convertir a lista y calcular porcentajes
        estudiantes_asistencia_lista = []
        for est_data in estudiantes_asistencia.values():
            porcentaje = (est_data['presentes'] / est_data['total'] * 100) if est_data['total'] > 0 else 0
            estudiantes_asistencia_lista.append({
                'estudiante': est_data['estudiante'],
                'nombre': est_data['nombre'],
                'total': est_data['total'],
                'presentes': est_data['presentes'],
                'ausentes': est_data['ausentes'],
                'justificados': est_data['justificados'],
                'porcentaje': round(porcentaje, 1),
                'estado': 'success' if porcentaje >= 85 else 'warning' if porcentaje >= 75 else 'danger'
            })

        # Ordenar por porcentaje de asistencia descendente
        estudiantes_asistencia_lista.sort(key=lambda x: x['porcentaje'], reverse=True)

        # Estadísticas por mes
        meses_asistencia = {}
        for asistencia in asistencias:
            mes = asistencia.fecha_registro.strftime('%Y-%m')
            if mes not in meses_asistencia:
                meses_asistencia[mes] = {
                    'mes': asistencia.fecha_registro.strftime('%B %Y'),
                    'total': 0,
                    'presentes': 0,
                    'ausentes': 0,
                    'justificados': 0
                }
            meses_asistencia[mes]['total'] += 1
            if asistencia.presente:
                meses_asistencia[mes]['presentes'] += 1
            else:
                meses_asistencia[mes]['ausentes'] += 1
            if asistencia.justificado:
                meses_asistencia[mes]['justificados'] += 1

        # Convertir a lista y calcular porcentajes
        meses_asistencia_lista = []
        for mes_data in meses_asistencia.values():
            porcentaje = (mes_data['presentes'] / mes_data['total'] * 100) if mes_data['total'] > 0 else 0
            meses_asistencia_lista.append({
                'mes': mes_data['mes'],
                'total': mes_data['total'],
                'presentes': mes_data['presentes'],
                'ausentes': mes_data['ausentes'],
                'justificados': mes_data['justificados'],
                'porcentaje': round(porcentaje, 1)
            })

        # Ordenar por mes descendente
        meses_asistencia_lista.sort(key=lambda x: x['mes'], reverse=True)

        context = {
            'asignatura': asignatura,
            'estudiantes': estudiantes,
            'clases': clases_formateadas,
            'estadisticas': estadisticas,
            'proximas_actividades': proximas_actividades,
            'comunicaciones': comunicaciones_formateadas,
            'temas_foro': temas_foro,
            'es_docente': request.user.usuario.auth_user == asignatura.docente.usuario.auth_user,
            'asistencias': asistencias,
            'estadisticas_asistencia': {
                'total_clases': total_clases,
                'total_registros': total_registros,
                'presentes': presentes,
                'ausentes': ausentes,
                'justificados': justificados,
                'porcentaje': round(porcentaje_asistencia, 1)
            },
            'estudiantes_asistencia': estudiantes_asistencia_lista,
            'meses_asistencia': meses_asistencia_lista
        }
        return render(request, 'teacher/asignatura_detalle.html', context)

    def post(self, request, asignatura_id):
        """
        Método para crear una nueva comunicación para la asignatura
        """
        asignatura = get_object_or_404(AsignaturaImpartida, id=asignatura_id)
        
        # Verificar que el usuario sea el profesor de la asignatura
        if not request.user.usuario.auth_user == asignatura.docente.usuario.auth_user:
            messages.error(request, 'No tienes permiso para crear comunicaciones en esta asignatura')
            return redirect('asignatura_detalle', asignatura_id=asignatura_id)
        
        # Obtener datos del formulario
        asunto = request.POST.get('asunto')
        contenido = request.POST.get('contenido')
        
        if not asunto or not contenido:
            messages.error(request, 'El asunto y contenido son obligatorios')
            return redirect('asignatura_detalle', asignatura_id=asignatura_id)
        
        try:
            with transaction.atomic():
                # Agregar el código de la asignatura al asunto
                asunto_completo = f'[{asignatura.codigo}] {asunto}'
                
                # Crear la comunicación
                comunicacion = Comunicacion.objects.create(
                    asunto=asunto_completo,
                    contenido=contenido,
                    autor=request.user
                )

                # Obtener todos los cursos que tienen esta asignatura
                cursos_asignatura = Curso.objects.filter(clases__asignatura_impartida=asignatura).distinct()
                
                # Agregar los cursos como destinatarios
                comunicacion.destinatarios_cursos.add(*cursos_asignatura)

                # Obtener todos los estudiantes de los cursos y agregarlos como destinatarios
                estudiantes_auth = []
                for curso in cursos_asignatura:
                    # Obtener los AuthUser de los estudiantes del curso
                    estudiantes_auth.extend([
                        est.usuario.auth_user 
                        for est in curso.estudiantes.select_related('usuario__auth_user').all()
                    ])
                
                # Agregar estudiantes como destinatarios
                if estudiantes_auth:
                    comunicacion.destinatarios_usuarios.add(*estudiantes_auth)
                
                messages.success(request, 'Comunicación enviada exitosamente')
                
        except Exception as e:
            messages.error(request, f'Error al crear la comunicación: {str(e)}')
            
        return redirect('asignatura_detalle', asignatura_id=asignatura_id)

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
def analisis_rendimiento(request, curso_id):
    """Analiza el rendimiento del curso usando datos reales"""
    try:
        # Obtener el curso y validar acceso
        try:
            curso = Curso.objects.get(id=curso_id)
        except Curso.DoesNotExist:
            return JsonResponse({"error": "Curso no encontrado"}, status=404)
            
        if not curso.tiene_acceso(request.user):
            return JsonResponse({"error": "No tiene permisos para acceder a este curso"}, status=403)

        # Obtener datos de evaluaciones
        evaluaciones = Evaluacion.objects.filter(clase__curso=curso)
        if not evaluaciones.exists():
            return JsonResponse({"error": "No hay evaluaciones registradas para este curso"}, status=404)
            
        notas_curso = AlumnoEvaluacion.objects.filter(evaluacion__in=evaluaciones)
        if not notas_curso.exists():
            return JsonResponse({"error": "No hay notas registradas para este curso"}, status=404)
        
        # Obtener datos de asistencia
        asistencias = Asistencia.objects.filter(estudiante__curso=curso)
        if not asistencias.exists():
            return JsonResponse({"error": "No hay registros de asistencia para este curso"}, status=404)
        
        # Calcular estadísticas
        total_estudiantes = curso.estudiantes.count()
        promedio_general = notas_curso.aggregate(Avg('nota'))['nota__avg'] or Decimal('0')
        asistencia_promedio = Decimal(str(asistencias.filter(presente=True).count() / asistencias.count() if asistencias.count() > 0 else 0))
        
        # Análisis de distribución de notas
        notas = list(notas_curso.values_list('nota', flat=True))
        distribucion = {
            'sobre_6': sum(1 for n in notas if n >= Decimal('6.0')),
            'entre_5_6': sum(1 for n in notas if Decimal('5.0') <= n < Decimal('6.0')),
            'entre_4_5': sum(1 for n in notas if Decimal('4.0') <= n < Decimal('5.0')),
            'bajo_4': sum(1 for n in notas if n < Decimal('4.0'))
        }

        # Análisis de tendencias
        notas_por_fecha = {}
        for eval in evaluaciones.order_by('fecha'):
            fecha = eval.fecha.strftime('%Y-%m-%d')
            notas_eval = AlumnoEvaluacion.objects.filter(evaluacion=eval)
            promedio = notas_eval.aggregate(Avg('nota'))['nota__avg'] or Decimal('0')
            notas_por_fecha[fecha] = float(promedio)  # Convertir a float para JSON
        
        tendencia = 'estable'
        if notas_por_fecha:
            valores = list(notas_por_fecha.values())
            if len(valores) > 1:
                diferencia = valores[-1] - valores[0]
                if diferencia > 0.3:
                    tendencia = 'mejorando'
                elif diferencia < -0.3:
                    tendencia = 'bajando'

        # Generar resumen usando los datos reales
        resumen = f"El curso presenta un promedio general de {float(promedio_general):.1f} con una asistencia promedio del {float(asistencia_promedio)*100:.1f}%. "
        resumen += f"La tendencia general del curso es '{tendencia}'. "
        
        if distribucion['bajo_4'] > total_estudiantes * 0.2:
            resumen += "Se observa un número significativo de estudiantes con rendimiento bajo 4.0, se recomienda implementar medidas de apoyo adicionales."
        elif distribucion['sobre_6'] > total_estudiantes * 0.3:
            resumen += "El curso muestra un excelente rendimiento con un alto porcentaje de estudiantes sobre 6.0."
        
        return JsonResponse({
            'resumen': resumen,
            'promedio_general': f"{float(promedio_general):.1f}",
            'asistencia_promedio': f"{float(asistencia_promedio)*100:.1f}%",
            'total_estudiantes': total_estudiantes,
            'distribucion': distribucion,
            'tendencia': tendencia,
            'notas_por_fecha': notas_por_fecha
        })

    except Exception as e:
        import traceback
        error_msg = f"Error al analizar rendimiento: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # Para el log del servidor
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def prediccion_riesgo(request, curso_id):
    """Identifica estudiantes en riesgo usando datos reales"""
    try:
        from decimal import Decimal
        
        # Obtener el curso y validar acceso
        try:
            curso = Curso.objects.get(id=curso_id)
        except Curso.DoesNotExist:
            return JsonResponse({"error": "Curso no encontrado"}, status=404)
            
        if not curso.tiene_acceso(request.user):
            return JsonResponse({"error": "No tiene permisos para acceder a este curso"}, status=403)

        estudiantes_riesgo = []
        total_riesgo = 0

        # Obtener datos históricos para cada estudiante
        for estudiante in curso.estudiantes.all():
            # Notas
            notas = list(AlumnoEvaluacion.objects.filter(
                estudiante=estudiante,
                evaluacion__clase__curso=curso
            ).values_list('nota', flat=True))
            
            # Asistencia
            asistencias = Asistencia.objects.filter(
                estudiante=estudiante,
                estudiante__curso=curso
            )
            porcentaje_asistencia = Decimal(str(asistencias.filter(presente=True).count() / asistencias.count())) if asistencias.count() > 0 else Decimal('0')
            
            # Calcular factores de riesgo
            factores = []
            promedio = Decimal(str(sum(notas) / len(notas))) if notas else Decimal('0')
            
            if promedio < Decimal('4.0'):
                factores.append(f"Promedio bajo ({float(promedio):.1f})")
            
            if porcentaje_asistencia < Decimal('0.85'):
                factores.append(f"Baja asistencia ({float(porcentaje_asistencia)*100:.1f}%)")
            
            # Tendencia de notas
            if len(notas) > 2:
                ultimas_tres = [Decimal(str(nota)) for nota in notas[-3:]]
                promedio_ultimas = sum(ultimas_tres) / len(ultimas_tres)
                if ultimas_tres[-1] < promedio_ultimas:
                    factores.append("Tendencia negativa en las últimas evaluaciones")

            # Determinar nivel de riesgo
            nivel_riesgo = 'bajo'
            if len(factores) >= 2:
                nivel_riesgo = 'alto'
            elif len(factores) == 1:
                nivel_riesgo = 'medio'

            if factores:
                estudiantes_riesgo.append({
                    'nombre': f"{estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno} {estudiante.usuario.apellido_materno}",
                    'nivel_riesgo': nivel_riesgo,
                    'factores': factores
                })
                total_riesgo += 1

        return JsonResponse({
            'total_riesgo': total_riesgo,
            'estudiantes': estudiantes_riesgo
        })

    except Exception as e:
        import traceback
        error_msg = f"Error al predecir riesgo: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # Para el log del servidor
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def obtener_recomendaciones(request, curso_id):
    """Genera recomendaciones personalizadas para los estudiantes del curso"""
    try:
        # Obtener el curso y validar acceso
        try:
            curso = Curso.objects.get(id=curso_id)
        except Curso.DoesNotExist:
            return JsonResponse({"error": "Curso no encontrado"}, status=404)
            
        if not curso.tiene_acceso(request.user):
            return JsonResponse({"error": "No tiene permisos para acceder a este curso"}, status=403)

        recomendaciones = []

        # Obtener datos históricos para cada estudiante
        for estudiante in curso.estudiantes.all():
            # Notas
            notas = list(AlumnoEvaluacion.objects.filter(
                estudiante=estudiante,
                evaluacion__clase__curso=curso
            ).values_list('nota', flat=True))
            
            # Asistencia
            asistencias = Asistencia.objects.filter(
                estudiante=estudiante,
                estudiante__curso=curso
            )
            porcentaje_asistencia = (asistencias.filter(presente=True).count() / asistencias.count()) if asistencias.count() > 0 else 0
            
            promedio = mean(notas) if notas else 0
            
            # Generar recomendaciones basadas en los datos
            if promedio < 4.0 or porcentaje_asistencia < 0.85:
                recomendacion = ""
                acciones = []

                if promedio < 4.0:
                    recomendacion = f"El estudiante presenta un promedio de {promedio:.1f}, lo cual es preocupante. "
                    acciones.extend([
                        "Programar sesiones de reforzamiento en las áreas más débiles",
                        "Implementar evaluaciones formativas adicionales",
                        "Establecer metas de mejora a corto plazo"
                    ])

                if porcentaje_asistencia < 0.85:
                    recomendacion += f"La asistencia del {porcentaje_asistencia*100:.1f}% está bajo lo esperado. "
                    acciones.extend([
                        "Contactar al apoderado para discutir la situación",
                        "Establecer un plan de recuperación de contenidos",
                        "Monitorear la asistencia diariamente"
                    ])

                recomendaciones.append({
                    'estudiante': f"{estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno} {estudiante.usuario.apellido_materno}",
                    'recomendacion': recomendacion,
                    'acciones': acciones
                })

        return JsonResponse({
            'recomendaciones': recomendaciones
        })

    except Exception as e:
        import traceback
        error_msg = f"Error al obtener recomendaciones: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # Para el log del servidor
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def generar_pdf(request):
    """Genera un PDF con el análisis solicitado"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from django.http import FileResponse
        import os
        from django.conf import settings
        import json
        import time
        
        data = json.loads(request.body)
        titulo = data.get('titulo', 'Reporte')
        contenido = data.get('contenido', '')
        
        # Crear directorio para PDFs si no existe
        pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Generar nombre único para el archivo
        filename = f"reporte_{request.user.id}_{int(time.time())}.pdf"
        filepath = os.path.join(pdf_dir, filename)
        
        # Crear el documento PDF
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Contenido del PDF
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        story.append(Paragraph(titulo, title_style))
        story.append(Spacer(1, 12))
        
        # Contenido principal
        content_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12
        )
        
        # Dividir el contenido en párrafos y escapar caracteres especiales
        paragraphs = contenido.split('\n')
        for p in paragraphs:
            if p.strip():
                # Escapar caracteres especiales de HTML
                p = p.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(p, content_style))
                story.append(Spacer(1, 12))
        
        # Generar el PDF
        doc.build(story)
        
        # Abrir y devolver el archivo como respuesta
        response = FileResponse(
            open(filepath, 'rb'),
            content_type='application/pdf',
            as_attachment=True,
            filename=filename
        )
        
        # Configurar para eliminar el archivo después de enviarlo
        response._resource_closers.append(lambda: os.unlink(filepath))
        
        return response

    except Exception as e:
        import traceback
        error_msg = f"Error al generar PDF: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # Para el log del servidor
        return JsonResponse({"error": f"Error al generar PDF: {str(e)}"}, status=500)

@method_decorator(login_required, name='dispatch')
class EliminarComunicacionView(View):
    def post(self, request, comunicacion_id):
        comunicacion = get_object_or_404(Comunicacion, id=comunicacion_id)
        
        # Verificar que el usuario sea el autor de la comunicación
        if comunicacion.autor != request.user:
            messages.error(request, 'No tienes permiso para eliminar esta comunicación')
            return JsonResponse({'status': 'error', 'message': 'No tienes permiso para eliminar esta comunicación'}, status=403)
        
        try:
            comunicacion.delete()
            return JsonResponse({'status': 'success', 'message': 'Comunicación eliminada exitosamente'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def get(self, request, comunicacion_id):
        return self.post(request, comunicacion_id)

@method_decorator(login_required, name='dispatch')
class ForoAsignaturaView(View):
    def get(self, request, asignatura_id):
        asignatura = get_object_or_404(AsignaturaImpartida, id=asignatura_id)
        
        # Verificar que el usuario tenga acceso a la asignatura
        if not (
            request.user.usuario.auth_user == asignatura.docente.usuario.auth_user or
            request.user.usuario.estudiante in asignatura.estudiantes_inscritos()
        ):
            messages.error(request, 'No tienes acceso a este foro')
            return redirect('home')
        
        # Obtener todos los temas del foro
        temas = ForoAsignatura.objects.filter(
            asignatura=asignatura
        ).select_related(
            'autor'
        ).prefetch_related(
            'mensajes', 
            'mensajes__autor'
        ).order_by('-es_anuncio', '-fecha')
        
        context = {
            'asignatura': asignatura,
            'temas': temas,
            'es_docente': request.user.usuario.auth_user == asignatura.docente.usuario.auth_user
        }
        return render(request, 'foro/foro_asignatura.html', context)

    def post(self, request, asignatura_id):
        asignatura = get_object_or_404(AsignaturaImpartida, id=asignatura_id)
        
        # Verificar que el usuario tenga acceso a la asignatura
        if not (
            request.user.usuario.auth_user == asignatura.docente.usuario.auth_user or
            request.user.usuario.estudiante in asignatura.estudiantes_inscritos()
        ):
            messages.error(request, 'No tienes acceso a este foro')
            return redirect('home')
        
        # Obtener datos del formulario
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        es_anuncio = request.POST.get('es_anuncio') == 'true' and request.user.usuario.auth_user == asignatura.docente.usuario.auth_user
        
        if not titulo or not contenido:
            messages.error(request, 'El título y contenido son obligatorios')
            return redirect('foro_asignatura', asignatura_id=asignatura_id)
        
        # Crear el tema
        ForoAsignatura.objects.create(
            titulo=titulo,
            contenido=contenido,
            autor=request.user.usuario,
            asignatura=asignatura,
            es_anuncio=es_anuncio
        )
        
        messages.success(request, 'Tema creado exitosamente')
        return redirect('foro_asignatura', asignatura_id=asignatura_id)

@method_decorator(login_required, name='dispatch')
class TemaForoAsignaturaView(View):
    def get(self, request, asignatura_id, tema_id):
        tema = get_object_or_404(ForoAsignatura, id=tema_id, asignatura_id=asignatura_id)
        
        # Verificar que el usuario tenga acceso a la asignatura
        if not (
            request.user.usuario.auth_user == tema.asignatura.docente.usuario.auth_user or
            request.user.usuario.estudiante in tema.asignatura.estudiantes_inscritos()
        ):
            messages.error(request, 'No tienes acceso a este tema')
            return redirect('home')
        
        context = {
            'tema': tema,
            'mensajes': tema.mensajes.select_related('autor').order_by('fecha'),
            'es_docente': request.user.usuario.auth_user == tema.asignatura.docente.usuario.auth_user
        }
        return render(request, 'foro/tema_asignatura.html', context)

    def post(self, request, asignatura_id, tema_id):
        tema = get_object_or_404(ForoAsignatura, id=tema_id, asignatura_id=asignatura_id)
        
        # Verificar que el usuario tenga acceso a la asignatura
        if not (
            request.user.usuario.auth_user == tema.asignatura.docente.usuario.auth_user or
            request.user.usuario.estudiante in tema.asignatura.estudiantes_inscritos()
        ):
            messages.error(request, 'No tienes acceso a este tema')
            return redirect('home')
        
        # Obtener contenido del mensaje
        contenido = request.POST.get('contenido')
        
        if not contenido:
            messages.error(request, 'El contenido es obligatorio')
            return redirect('tema_foro_asignatura', asignatura_id=asignatura_id, tema_id=tema_id)
        
        # Crear el mensaje
        MensajeForoAsignatura.objects.create(
            foro=tema,
            autor=request.user.usuario,
            contenido=contenido
        )
        
        messages.success(request, 'Respuesta enviada exitosamente')
        return redirect('tema_foro_asignatura', asignatura_id=asignatura_id, tema_id=tema_id)

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


