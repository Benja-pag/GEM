from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from Core.models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura, AsignaturaImpartida, Curso, AsignaturaInscrita, Evaluacion, AlumnoEvaluacion, EvaluacionBase
from django.db.models import Count, Avg
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

