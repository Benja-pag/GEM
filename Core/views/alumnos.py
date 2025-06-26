from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from Core.models import  Estudiante, Asistencia, Clase, Foro, AuthUser, Asignatura, AsignaturaImpartida, Curso, AsignaturaInscrita, Comunicacion
from django.db.models import  Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from Core.servicios.repos.asignaturas import get_asignaturas_estudiante
from Core.servicios.repos.cursos import get_estudiantes_por_curso
from datetime import datetime, date, timedelta

from Core.servicios.alumnos.helpers import (
    get_horario_estudiante,
    get_evaluaciones_estudiante,
    get_promedio_estudiante,
    get_asistencia_estudiante,
    get_eventos_calendario,
)

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
        
        # Calcular datos generales para las tarjetas de resumen
        # Datos generales de asistencia
        asistencia_general = {
            'total': 0,
            'presentes': 0,
            'porcentaje': 0.0
        }
        for asignatura_data in asistencia_estudiante.values():
            asistencia_general['total'] += asignatura_data['total']
            asistencia_general['presentes'] += asignatura_data['presentes']
        
        if asistencia_general['total'] > 0:
            asistencia_general['porcentaje'] = (asistencia_general['presentes'] / asistencia_general['total']) * 100
        
        # Calcular evaluaciones pendientes (evaluaciones futuras)
        evaluaciones_pendientes = 0
        evaluaciones_data = get_evaluaciones_estudiante(estudiante_obj.pk)
        for asignatura_evaluaciones in evaluaciones_data.values():
            for evaluacion in asignatura_evaluaciones:
                if evaluacion['fecha'] > date.today():
                    evaluaciones_pendientes += 1
        
        context = {
            'alumno' : usuario,
            'curso' : curso,
            'estudiantes_curso': estudiantes_curso,
            'asignaturas_estudiante': asignaturas_estudiante,
            'horario_estudiante': horario_estudiante,
            'evaluaciones_estudiante': evaluaciones_estudiante,
            'promedio_estudiante': promedio_estudiante,
            'asistencia_estudiante': asistencia_general,
            'evaluaciones_estudiante': {
                'pendientes': evaluaciones_pendientes,
                'detalle': evaluaciones_data
            },
            'eventos_calendario': get_eventos_calendario(estudiante_obj.pk),
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
        evaluaciones_data = get_evaluaciones_estudiante(estudiante_obj.pk)
        
        # Calcular datos generales para las tarjetas de resumen
        # Datos generales de asistencia
        asistencia_general = {
            'total': 0,
            'presentes': 0,
            'porcentaje': 0.0
        }
        for asignatura_data in asistencia_estudiante.values():
            asistencia_general['total'] += asignatura_data['total']
            asistencia_general['presentes'] += asignatura_data['presentes']
        
        if asistencia_general['total'] > 0:
            asistencia_general['porcentaje'] = (asistencia_general['presentes'] / asistencia_general['total']) * 100
        
        # Calcular evaluaciones pendientes (evaluaciones futuras)
        evaluaciones_pendientes = 0
        for asignatura_evaluaciones in evaluaciones_data.values():
            for evaluacion in asignatura_evaluaciones:
                if evaluacion['fecha'] > date.today():
                    evaluaciones_pendientes += 1
        
        # Obtener temas del foro
        temas_foro = Foro.objects.all().order_by('-fecha', '-hora')[:5] # Obtener los 5 más recientes

        # Obtener las últimas comunicaciones no leídas
        comunicaciones_no_leidas = Comunicacion.objects.filter(
            Q(destinatarios_usuarios=request.user) | Q(destinatarios_cursos=estudiante_obj.curso)
        ).exclude(leido_por=request.user).distinct().order_by('-fecha_envio')[:5]

        context = {
            'alumno' : usuario,
            'curso' : curso,
            'estudiantes_curso': estudiantes_curso,
            'asignaturas_estudiante': asignaturas_estudiante,
            'horario_estudiante': horario_estudiante,
            'evaluaciones_estudiante': evaluaciones_data,  # Datos originales para las pestañas
            'promedio_estudiante': promedio_estudiante,
            'asistencia_estudiante': asistencia_estudiante,  # Datos originales para las pestañas
            'asistencia_general': asistencia_general,  # Datos generales para las tarjetas
            'evaluaciones_pendientes': evaluaciones_pendientes,  # Para las tarjetas
            'eventos_calendario': get_eventos_calendario(estudiante_obj.pk),
            'electivos_disponibles': electivos_disponibles,
            'mostrar_electivos': mostrar_electivos,
            'electivos_inscritos': electivos_inscritos,
            'temas_foro': temas_foro,
            'comunicaciones_no_leidas': comunicaciones_no_leidas,
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

