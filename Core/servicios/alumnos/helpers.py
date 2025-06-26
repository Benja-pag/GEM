from Core.models import (
    AsignaturaInscrita, Clase, AlumnoEvaluacion, Asistencia, Estudiante,
    CalendarioColegio, CalendarioClase, HorarioCurso, Asignatura
)
from django.db.models import Avg
from datetime import date, timedelta
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
    
    # Obtener todas las asignaturas inscritas del estudiante
    asignaturas_inscritas = AsignaturaInscrita.objects.filter(
        estudiante_id=estudiante_id,
        validada=True
    ).select_related('asignatura_impartida__asignatura')
    
    # Inicializar diccionario con todas las asignaturas
    asistencia_por_asignatura = {}
    for inscripcion in asignaturas_inscritas:
        asignatura_nombre = inscripcion.asignatura_impartida.asignatura.nombre
        asistencia_por_asignatura[asignatura_nombre] = {
            'total': 0,
            'presentes': 0,
            'ausentes': 0,
            'justificados': 0,
            'porcentaje': 0.0,
            'sin_registro': True  # Marcar como sin registro inicialmente
        }
    
    # Obtener asistencias del estudiante para el mes
    asistencias = Asistencia.objects.filter(
        estudiante_id=estudiante_id,
        fecha_registro__date__gte=primer_dia,
        fecha_registro__date__lte=ultimo_dia
    ).select_related('clase__asignatura_impartida__asignatura')
    
    # Procesar las asistencias existentes
    for asistencia in asistencias:
        asignatura_nombre = asistencia.clase.asignatura_impartida.asignatura.nombre
        if asignatura_nombre in asistencia_por_asignatura:
            asistencia_por_asignatura[asignatura_nombre]['sin_registro'] = False
            asistencia_por_asignatura[asignatura_nombre]['total'] += 1
            if asistencia.presente:
                asistencia_por_asignatura[asignatura_nombre]['presentes'] += 1
            else:
                asistencia_por_asignatura[asignatura_nombre]['ausentes'] += 1
                if asistencia.justificado:
                    asistencia_por_asignatura[asignatura_nombre]['justificados'] += 1
    
    # Calcular porcentajes solo para asignaturas con registros
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

