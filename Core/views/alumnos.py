from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from Core.models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura, AsignaturaImpartida, Curso, AsignaturaInscrita, Evaluacion, AlumnoEvaluacion, EvaluacionBase, HorarioCurso
from django.db.models import Count, Avg, Q
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
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
from Core.servicios.repos.asignaturas import get_asignaturas_estudiante
from Core.servicios.repos.cursos import get_estudiantes_por_curso
from datetime import datetime, date, timedelta
from collections import defaultdict
import json
import calendar

def get_horario_estudiante(estudiante_id):
    """
    Obtiene el horario completo del estudiante basado en sus asignaturas inscritas
    """
    # Obtener las asignaturas inscritas del estudiante
    asignaturas_inscritas = AsignaturaInscrita.objects.filter(
        estudiante=estudiante_id,
        validada=True
    ).select_related(
        'asignatura_impartida__asignatura',
        'asignatura_impartida__docente__usuario'
    )
    
    # Obtener todas las clases de las asignaturas inscritas
    horario = {}
    dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
    bloques = ['1', '2', 'RECREO1', '3', '4', 'RECREO2', '5', '6', 'ALMUERZO', '7', '8', '9']
    
    # Inicializar el horario vacío
    for dia in dias:
        horario[dia] = {}
        for bloque in bloques:
            horario[dia][bloque] = None
    
    # Llenar el horario con las clases
    for inscripcion in asignaturas_inscritas:
        clases = Clase.objects.filter(
            asignatura_impartida=inscripcion.asignatura_impartida
        ).select_related('asignatura_impartida__asignatura', 'asignatura_impartida__docente__usuario')
        
        for clase in clases:
            if clase.fecha in horario and clase.horario in horario[clase.fecha]:
                horario[clase.fecha][clase.horario] = {
                    'asignatura': clase.asignatura_impartida.asignatura.nombre,
                    'docente': f"{clase.asignatura_impartida.docente.usuario.nombre} {clase.asignatura_impartida.docente.usuario.apellido_paterno}",
                    'sala': clase.sala,
                    'codigo': clase.asignatura_impartida.codigo
                }
    
    return horario

def get_evaluaciones_estudiante(estudiante_id):
    """
    Obtiene todas las evaluaciones y notas del estudiante
    """
    evaluaciones_estudiante = AlumnoEvaluacion.objects.filter(
        estudiante_id=estudiante_id
    ).select_related(
        'evaluacion__evaluacion_base__asignatura',
        'evaluacion__clase__asignatura_impartida__asignatura',
        'evaluacion__clase__curso'
    ).order_by(
        'evaluacion__evaluacion_base__asignatura__nombre',
        'evaluacion__evaluacion_base__nombre',
        'evaluacion__fecha'
    )
    
    # Agrupar por asignatura y tipo de evaluación para evitar duplicados
    evaluaciones_por_asignatura = {}
    for evaluacion in evaluaciones_estudiante:
        asignatura_nombre = evaluacion.evaluacion.evaluacion_base.asignatura.nombre
        tipo_evaluacion = evaluacion.evaluacion.evaluacion_base.nombre
        
        if asignatura_nombre not in evaluaciones_por_asignatura:
            evaluaciones_por_asignatura[asignatura_nombre] = {}
        
        # Solo agregar si no existe ya este tipo de evaluación para esta asignatura
        if tipo_evaluacion not in evaluaciones_por_asignatura[asignatura_nombre]:
            evaluaciones_por_asignatura[asignatura_nombre][tipo_evaluacion] = {
                'nombre': evaluacion.evaluacion.evaluacion_base.nombre,
                'fecha': evaluacion.evaluacion.fecha,
                'nota': evaluacion.nota,
                'ponderacion': evaluacion.evaluacion.evaluacion_base.ponderacion,
                'estado': 'Aprobado' if evaluacion.nota >= 4.0 else 'Reprobado',
                'observaciones': evaluacion.observaciones
            }
    
    # Convertir el diccionario anidado a una lista plana para cada asignatura
    resultado = {}
    for asignatura, evaluaciones in evaluaciones_por_asignatura.items():
        resultado[asignatura] = list(evaluaciones.values())
    
    return resultado

def get_promedio_estudiante(estudiante_id):
    """
    Calcula el promedio general del estudiante
    """
    promedio = AlumnoEvaluacion.objects.filter(
        estudiante_id=estudiante_id
    ).aggregate(
        promedio=Avg('nota')
    )['promedio']
    
    return promedio if promedio else 0.0

def get_asistencia_estudiante(estudiante_id):
    """
    Obtiene los datos de asistencia del estudiante para el mes actual
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
    
    # Obtener asistencias del estudiante para el mes
    asistencias = Asistencia.objects.filter(
        estudiante_id=estudiante_id,
        fecha_registro__date__gte=primer_dia,
        fecha_registro__date__lte=ultimo_dia
    ).select_related('clase__asignatura_impartida__asignatura')
    
    # Agrupar por asignatura
    asistencia_por_asignatura = {}
    for asistencia in asistencias:
        asignatura_nombre = asistencia.clase.asignatura_impartida.asignatura.nombre
        if asignatura_nombre not in asistencia_por_asignatura:
            asistencia_por_asignatura[asignatura_nombre] = {
                'total': 0,
                'presentes': 0,
                'ausentes': 0,
                'justificados': 0,
                'porcentaje': 0.0
            }
        
        asistencia_por_asignatura[asignatura_nombre]['total'] += 1
        if asistencia.presente:
            asistencia_por_asignatura[asignatura_nombre]['presentes'] += 1
        else:
            asistencia_por_asignatura[asignatura_nombre]['ausentes'] += 1
            if asistencia.justificado:
                asistencia_por_asignatura[asignatura_nombre]['justificados'] += 1
    
    # Calcular porcentajes
    for asignatura in asistencia_por_asignatura.values():
        if asignatura['total'] > 0:
            asignatura['porcentaje'] = (asignatura['presentes'] / asignatura['total']) * 100
    
    return asistencia_por_asignatura

def get_eventos_calendario(estudiante_id):
    """
    Obtiene los eventos del calendario para un estudiante.
    Incluye eventos del colegio, de las asignaturas inscritas y el horario de clases.
    """
    try:
        estudiante = Estudiante.objects.get(pk=estudiante_id)
        
        # --- Obtener eventos de CalendarioClase y CalendarioColegio ---
        asignaturas_ids = AsignaturaInscrita.objects.filter(
            estudiante=estudiante
        ).values_list('asignatura_impartida__asignatura_id', flat=True)

        eventos = []
        # Eventos del colegio
        eventos_colegio = CalendarioColegio.objects.all()
        for evento in eventos_colegio:
            eventos.append({
                'id': f'colegio_{evento.pk}',
                'title': evento.nombre_actividad,
                'start': f'{evento.fecha}T{evento.hora}',
                'description': evento.descripcion,
                'color': '#0dcaf0', # Azul claro para eventos del colegio
                'extendedProps': {
                    'type': 'Colegio',
                    'encargado': evento.encargado,
                    'ubicacion': evento.ubicacion,
                }
            })

        # Eventos de las clases del estudiante, filtrando por los IDs de asignatura
        eventos_clase = CalendarioClase.objects.filter(
            asignatura_id__in=list(asignaturas_ids)
        )
        for evento in eventos_clase:
            eventos.append({
                'id': f'clase_{evento.pk}',
                'title': f"{evento.nombre_actividad} - {evento.asignatura.nombre}",
                'start': f'{evento.fecha}T{evento.hora if evento.hora else "00:00:00"}',
                'description': evento.descripcion,
                'color': '#198754', # Verde para evaluaciones
                'extendedProps': {
                    'type': 'Asignatura',
                    'materia': evento.asignatura.nombre
                }
            })
        
        # --- Generar eventos recurrentes del horario de clases (deshabilitado) ---
        # if estudiante.curso:
        #     hoy = date.today()
        #     # Generar eventos para el mes actual, el anterior y el siguiente
        #     for i in range(-1, 2):
        #         mes = hoy.month + i
        #         año = hoy.year
        #         if mes == 0:
        #             mes = 12
        #             año -= 1
        #         elif mes == 13:
        #             mes = 1
        #             año += 1
                
        #         # Obtener todos los días del mes
        #         dias_del_mes = calendar.monthrange(año, mes)[1]
        #         for dia_num in range(1, dias_del_mes + 1):
        #             fecha_actual = date(año, mes, dia_num)
        #             dia_semana_num = fecha_actual.weekday() # Lunes=0, Domingo=6
        #             dias_semana = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
        #             dia_semana_str = dias_semana[dia_semana_num]

        #             # Obtener las clases del estudiante para ese día de la semana
        #             clases_del_dia = Clase.objects.filter(
        #                 asignatura_impartida__inscripciones__estudiante=estudiante,
        #                 asignatura_impartida__inscripciones__validada=True,
        #                 fecha=dia_semana_str
        #             ).select_related(
        #                 'asignatura_impartida__asignatura',
        #                 'asignatura_impartida__docente__usuario'
        #             ).distinct()

        #             for clase in clases_del_dia:
        #                 # Mapear el número de bloque a la hora real usando HorarioCurso
        #                 try:
        #                     bloque_numero = clase.horario
        #                     # Buscar el bloque correspondiente en HorarioCurso
        #                     bloque_info = HorarioCurso.objects.filter(
        #                         bloque=bloque_numero,
        #                         dia=dia_semana_str,
        #                         actividad='CLASE'
        #                     ).first()
                            
        #                     if bloque_info:
        #                         # Extraer la hora de inicio del bloque (formato: "08:00 - 08:45")
        #                         hora_inicio = bloque_info.get_bloque_display().split(' - ')[0]
        #                     else:
        #                         # Si no encuentra el bloque, usar un mapeo por defecto
        #                         mapeo_bloques = {
        #                             '1': '08:00', '2': '08:45', '3': '09:45', '4': '10:30',
        #                             '5': '11:30', '6': '12:15', '7': '13:45', '8': '14:30', '9': '15:15'
        #                         }
        #                         hora_inicio = mapeo_bloques.get(bloque_numero, '08:00')
        #                 except:
        #                     hora_inicio = "08:00"  # Hora por defecto
                        
        #                 eventos.append({
        #                     'title': f"{clase.asignatura_impartida.asignatura.nombre} - {clase.sala}",
        #                     'start': f'{fecha_actual}T{hora_inicio}:00',
        #                     'allDay': False,
        #                     'display': 'block',
        #                     'color': '#6c757d', # Gris para las clases regulares
        #                     'extendedProps': {
        #                         'type': 'Clase',
        #                         'docente': f"{clase.asignatura_impartida.docente.usuario.nombre} {clase.asignatura_impartida.docente.usuario.apellido_paterno}",
        #                         'sala': clase.sala,
        #                         'asignatura': clase.asignatura_impartida.asignatura.nombre
        #                     }
        #                 })

        return json.dumps(eventos)

    except Estudiante.DoesNotExist:
        return json.dumps([])

@method_decorator(login_required, name='dispatch')
class EstudiantePanelView(View):
    def get(self, request):
        if not hasattr(request.user.usuario, 'estudiante'):
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        usuario = request.user.usuario
        estudiante_obj = usuario.estudiante

        curso = usuario.estudiante.curso
        estudiantes_curso = get_estudiantes_por_curso(usuario.estudiante.curso_id)
        asignaturas_estudiante = get_asignaturas_estudiante(usuario.pk)
        horario_estudiante = get_horario_estudiante(usuario.auth_user_id)
        evaluaciones_estudiante = get_evaluaciones_estudiante(estudiante_obj.pk)
        promedio_estudiante = get_promedio_estudiante(estudiante_obj.pk)
        asistencia_estudiante = get_asistencia_estudiante(estudiante_obj.pk)
        
        context = {
            'alumno' : usuario,
            'curso' : curso,
            'estudiantes_curso': estudiantes_curso,
            'asignaturas_estudiante': asignaturas_estudiante,
            'horario_estudiante': horario_estudiante,
            'evaluaciones_estudiante': evaluaciones_estudiante,
            'promedio_estudiante': promedio_estudiante,
            'asistencia_estudiante': asistencia_estudiante
        }
        
        return render(request, 'student_panel.html', context)

@method_decorator(login_required, name='dispatch')
class EstudiantePanelModularView(View):
    def get(self, request):
        if not hasattr(request.user.usuario, 'estudiante'):
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        usuario = request.user.usuario
        estudiante_obj = usuario.estudiante
        curso = usuario.estudiante.curso

        # Lógica para obtener electivos y decidir si se muestra la pestaña
        electivos_disponibles = []
        mostrar_electivos = False
        if curso and curso.nivel in [3, 4]:
            mostrar_electivos = True
            electivos_disponibles = Asignatura.objects.filter(
                es_electivo=True,
                nivel=curso.nivel,
                imparticiones__isnull=False,
                imparticiones__docente__isnull=False,
                imparticiones__clases__isnull=False
            ).distinct().prefetch_related(
                'imparticiones__docente__usuario', 
                'imparticiones__clases'
            )

        # Obtener los electivos en los que el estudiante ya está inscrito
        electivos_inscritos = AsignaturaInscrita.objects.filter(
            estudiante=estudiante_obj,
            asignatura_impartida__asignatura__es_electivo=True,
            validada=True
        ).select_related(
            'asignatura_impartida__asignatura', 
            'asignatura_impartida__docente__usuario'
        ).prefetch_related(
            'asignatura_impartida__clases'
        )
        
        # Si hay electivos inscritos, obtener compañeros y contar cupos
        if electivos_inscritos:
            for inscripcion in electivos_inscritos:
                impartida = inscripcion.asignatura_impartida
                # Contar cupos
                inscripcion.cupos_actuales = AsignaturaInscrita.objects.filter(asignatura_impartida=impartida, validada=True).count()
                # Obtener compañeros (excluyendo al propio estudiante)
                inscripcion.compañeros = AsignaturaInscrita.objects.filter(
                    asignatura_impartida=impartida, validada=True
                ).exclude(estudiante=estudiante_obj).select_related('estudiante__usuario')

        estudiantes_curso = get_estudiantes_por_curso(usuario.estudiante.curso_id)
        asignaturas_estudiante = get_asignaturas_estudiante(usuario.pk)
        horario_estudiante = get_horario_estudiante(usuario.auth_user_id)
        evaluaciones_estudiante = get_evaluaciones_estudiante(estudiante_obj.pk)
        promedio_estudiante = get_promedio_estudiante(estudiante_obj.pk)
        asistencia_estudiante = get_asistencia_estudiante(estudiante_obj.pk)
        
        context = {
            'alumno' : usuario,
            'curso' : curso,
            'estudiantes_curso': estudiantes_curso,
            'asignaturas_estudiante': asignaturas_estudiante,
            'horario_estudiante': horario_estudiante,
            'evaluaciones_estudiante': evaluaciones_estudiante,
            'promedio_estudiante': promedio_estudiante,
            'asistencia_estudiante': asistencia_estudiante,
            'eventos_calendario': get_eventos_calendario(estudiante_obj.pk),
            'electivos_disponibles': electivos_disponibles,
            'mostrar_electivos': mostrar_electivos,
            'electivos_inscritos': electivos_inscritos,
        }
        
        return render(request, 'student_panel_modular.html', context)

@method_decorator(login_required, name='dispatch')
class AttendanceView(View):
    template_name = 'attendance.html'
    
    def get(self, request):
        if not (request.user.is_admin or hasattr(request.user.usuario, 'docente')):
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        
        # Obtener fecha actual si no se especifica una
        fecha = request.GET.get('fecha')
        if not fecha:
            fecha = timezone.now().date()
        else:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        # Obtener el día de la semana (0 = Lunes, 6 = Domingo)
        dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
        dia_semana = dias[fecha.weekday()]
        
        print(f"Fecha: {fecha}")
        print(f"Día de la semana: {dia_semana}")
        
        # Obtener asignaturas del profesor para el día
        if request.user.is_admin:
            asignaturas = AsignaturaImpartida.objects.filter(
                clases__fecha=dia_semana
            ).select_related('asignatura', 'docente__usuario').distinct()
        else:
            docente = request.user.usuario.docente
            asignaturas = AsignaturaImpartida.objects.filter(
                docente=docente,
                clases__fecha=dia_semana
            ).select_related('asignatura', 'docente__usuario').distinct()
        
        print(f"Asignaturas encontradas: {len(asignaturas)}")
        for asignatura in asignaturas:
            print(f"- {asignatura.asignatura.nombre} - {asignatura.docente.usuario.nombre} {asignatura.docente.usuario.apellido_paterno}")
        
        # Obtener cursos disponibles para las asignaturas
        cursos = []
        for asignatura in asignaturas:
            cursos_asignatura = Curso.objects.filter(
                clases__asignatura_impartida=asignatura,
                clases__fecha=dia_semana
            ).distinct()
            for curso in cursos_asignatura:
                curso.asignatura_impartida = asignatura
                cursos.append(curso)
        
        print(f"Cursos encontrados: {len(cursos)}")
        for curso in cursos:
            print(f"- {curso.nivel}°{curso.letra}")
        
        # Si hay asignaturas, seleccionar la primera por defecto
        asignatura_id = request.GET.get('asignatura')
        if not asignatura_id and len(asignaturas) > 0:
            asignatura_id = asignaturas.first().id
        
        # Obtener estudiantes
        estudiantes = []
        if asignatura_id:
            curso_id = request.GET.get('curso')
            if not curso_id and len(cursos) > 0:
                curso_id = cursos[0].id
                
            if curso_id:
                estudiantes = Estudiante.objects.filter(
                    curso_id=curso_id,
                    asignaturas_inscritas__asignatura_impartida_id=asignatura_id,
                    asignaturas_inscritas__validada=True
                ).select_related('usuario')
        
        print(f"Estudiantes encontrados: {len(estudiantes)}")
        
        context = {
            'fecha': fecha,
            'cursos': cursos,
            'asignaturas': asignaturas,
            'estudiantes': estudiantes,
            'curso_seleccionado': curso_id if 'curso_id' in locals() else None,
            'asignatura_seleccionada': asignatura_id
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        if not (request.user.is_admin or hasattr(request.user.usuario, 'docente')):
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        
        fecha = request.POST.get('fecha', timezone.now().date())
        curso_id = request.POST.get('curso')
        asignatura_id = request.POST.get('asignatura')
        
        if not all([fecha, curso_id, asignatura_id]):
            messages.error(request, 'Faltan datos necesarios para registrar la asistencia')
            return redirect('attendance')
        
        # Obtener la clase o crearla si no existe
        clase, created = Clase.objects.get_or_create(
            fecha=fecha,
            asignatura_impartida_id=asignatura_id,
            curso_id=curso_id,
            defaults={
                'horario': '08:00-09:00',  # Horario por defecto
                'sala': 'Sala Principal'   # Sala por defecto
            }
        )
        
        # Registrar asistencia para cada estudiante
        for key, value in request.POST.items():
            if key.startswith('estado_'):
                estudiante_id = key.split('_')[1]
                estado = value
                observacion = request.POST.get(f'observacion_{estudiante_id}', '')
                
                # Crear o actualizar el registro de asistencia
                Asistencia.objects.update_or_create(
                    clase=clase,
                    estudiante_id=estudiante_id,
                    defaults={
                        'presente': estado == 'presente',
                        'justificado': estado == 'justificado',
                        'observaciones': observacion
                    }
                )
        
        messages.success(request, 'Asistencia registrada exitosamente')
        return redirect('attendance')

@method_decorator(csrf_exempt, name='dispatch')
class InscribirElectivoView(View):
    def post(self, request):
        if not hasattr(request.user.usuario, 'estudiante'):
            return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
        usuario = request.user.usuario
        estudiante = usuario.estudiante
        asignatura_id = request.POST.get('asignatura_id')
        accion = request.POST.get('accion')  # 'inscribir' o 'desinscribir'
        if not asignatura_id or accion not in ['inscribir', 'desinscribir']:
            return JsonResponse({'success': False, 'error': 'Datos incompletos'})
        try:
            asignatura = Asignatura.objects.get(pk=asignatura_id, es_electivo=True, nivel=estudiante.curso.nivel)
        except Asignatura.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Electivo no válido para tu nivel'})
        # Buscar la AsignaturaImpartida (puede haber varias, tomamos la primera)
        impartida = asignatura.imparticiones.first()
        if not impartida:
            return JsonResponse({'success': False, 'error': 'No hay grupo disponible para este electivo'})
        if accion == 'inscribir':
            # Contar electivos inscritos
            electivos_actuales = AsignaturaInscrita.objects.filter(
                estudiante=estudiante,
                asignatura_impartida__asignatura__es_electivo=True,
                validada=True
            ).count()
            if electivos_actuales >= 3:
                return JsonResponse({'success': False, 'error': 'Ya tienes 3 electivos inscritos'})
            # Inscribir si no está inscrito
            insc, created = AsignaturaInscrita.objects.get_or_create(
                estudiante=estudiante,
                asignatura_impartida=impartida,
                defaults={'validada': True}
            )
            if not created and not insc.validada:
                insc.validada = True
                insc.save()
            return JsonResponse({'success': True, 'accion': 'inscrito'})
        else:  # desinscribir
            try:
                insc = AsignaturaInscrita.objects.get(
                    estudiante=estudiante,
                    asignatura_impartida=impartida,
                    validada=True
                )
                insc.validada = False
                insc.save()
                return JsonResponse({'success': True, 'accion': 'desinscrito'})
            except AsignaturaInscrita.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'No estabas inscrito en este electivo'})

@method_decorator(csrf_exempt, name='dispatch')
class InscribirElectivosLoteView(View):
    @transaction.atomic
    def post(self, request):
        if not hasattr(request.user.usuario, 'estudiante'):
            return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)

        estudiante = request.user.usuario.estudiante
        ids_electivos_str = request.POST.getlist('electivos[]')

        # 1. Validación de cantidad
        if len(ids_electivos_str) != 4:
            return JsonResponse({'success': False, 'error': f'Debes seleccionar exactamente 4 electivos. Has seleccionado {len(ids_electivos_str)}.'})

        # 2. Validación de IDs y obtención de horarios
        horarios_seleccionados = set()
        electivos_a_inscribir = []
        
        try:
            ids_electivos = [int(id_str) for id_str in ids_electivos_str]
            asignaturas = Asignatura.objects.filter(pk__in=ids_electivos, es_electivo=True, nivel=estudiante.curso.nivel)

            if asignaturas.count() != 4:
                return JsonResponse({'success': False, 'error': 'Alguno de los electivos seleccionados no es válido para tu nivel.'})

            for asignatura in asignaturas:
                clase_info = Clase.objects.filter(asignatura_impartida__asignatura=asignatura).first()
                if not clase_info:
                    return JsonResponse({'success': False, 'error': f'El electivo "{asignatura.nombre}" no tiene un horario definido.'})

                # Crear clave única para día y bloque
                horario_clave = f"{clase_info.fecha}-{clase_info.horario}"
                if horario_clave in horarios_seleccionados:
                    return JsonResponse({'success': False, 'error': f'Hay un choque de horario. Tienes más de un electivo seleccionado el {clase_info.get_fecha_display()} en el bloque {clase_info.horario}.'})
                
                horarios_seleccionados.add(horario_clave)
                impartida = AsignaturaImpartida.objects.get(asignatura=asignatura)
                electivos_a_inscribir.append(impartida)

        except (ValueError, AsignaturaImpartida.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Ocurrió un error con los datos enviados.'})

        # 3. Proceso de inscripción (atómico gracias al decorador)
        # Borrar inscripciones de electivos anteriores
        AsignaturaInscrita.objects.filter(
            estudiante=estudiante,
            asignatura_impartida__asignatura__es_electivo=True
        ).delete()

        # Inscribir los nuevos
        for impartida in electivos_a_inscribir:
            AsignaturaInscrita.objects.create(
                estudiante=estudiante,
                asignatura_impartida=impartida,
                validada=True
            )

        return JsonResponse({'success': True, 'message': '¡Felicitaciones! Has sido inscrito en tus 4 electivos.'})

@method_decorator(csrf_exempt, name='dispatch')
class BorrarInscripcionElectivosView(View):
    def post(self, request):
        if not hasattr(request.user.usuario, 'estudiante'):
            return redirect('home') # O mostrar un error

        estudiante = request.user.usuario.estudiante
        
        # Borrar todas las inscripciones a electivos
        AsignaturaInscrita.objects.filter(
            estudiante=estudiante,
            asignatura_impartida__asignatura__es_electivo=True
        ).delete()

        messages.success(request, 'Tu selección de electivos ha sido reiniciada. Ahora puedes volver a escoger.')
        return redirect('estudiante_panel')

