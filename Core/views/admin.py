from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from Core.models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura, AsignaturaImpartida, Curso, ProfesorJefe, Especialidad, Comunicacion
from django.db.models import Count, Avg, Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from Core.servicios.repos import usuarios
from Core.servicios.helpers import validadores, serializadores
from Core.servicios.repos.usuarios import crear_usuario, actualizar_usuario
from Core.servicios.repos.cursos import get_curso, get_estudiantes_por_curso
from django.http import JsonResponse
import json
from datetime import datetime, date
from Core.models.notas import Evaluacion, AlumnoEvaluacion

def get_eventos_calendario_admin():
    """
    Obtiene todos los eventos del colegio para el administrador
    """
    try:
        eventos = []
        
        # Mapeo de colores para diferentes tipos de eventos
        COLOR_MAPPING = {
            'REUNION': '#6f42c1',
            'EVALUACION': '#dc3545', 
            'TAREA': '#fd7e14',
            'MATERIAL': '#20c997',
            'ENTREGA': '#0d6efd',
            'EVENTO_COLEGIO': '#6610f2',
            'CAPACITACION': '#d63384',
            'CANCELAR_CLASE': '#dc3545',
            'OTRO': '#6c757d'
        }
        
        # Eventos del colegio (institucionales)
        eventos_colegio = CalendarioColegio.objects.all()
        for evento in eventos_colegio:
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
                    'puede_editar': True,  # Admin puede editar todos
                    'puede_eliminar': True
                }
            })
        
        # Eventos de todas las clases con información de curso
        eventos_clases = CalendarioClase.objects.all().select_related('asignatura')
        for evento in eventos_clases:
            # Intentar obtener información del curso a través de AsignaturaImpartida
            curso_info = 'Sin curso'
            try:
                # Buscar AsignaturaImpartida relacionada para obtener el curso
                from Core.models import AsignaturaImpartida, Clase
                asignatura_impartida = AsignaturaImpartida.objects.filter(
                    asignatura=evento.asignatura
                ).first()
                
                if asignatura_impartida:
                    # Buscar clases relacionadas para obtener el curso
                    clase = Clase.objects.filter(
                        asignatura_impartida=asignatura_impartida
                    ).first()
                    
                    if clase and clase.curso:
                        curso_info = f"{clase.curso.nivel}°{clase.curso.letra}"
            except:
                pass
            
            eventos.append({
                'id': f'clase_{evento.pk}',
                'title': f"{evento.nombre_actividad} - {evento.asignatura.nombre}",
                'start': f'{evento.fecha}T{evento.hora if evento.hora else "00:00:00"}',
                'description': evento.descripcion,
                'color': '#198754',  # Verde para eventos de clases
                'extendedProps': {
                    'type': 'Asignatura',
                    'materia': evento.asignatura.nombre,
                    'curso': curso_info,
                    'puede_editar': True,  # Admin puede editar todos
                    'puede_eliminar': True
                }
            })
        

        return eventos

    except Exception as e:
        print(f"Error en get_eventos_calendario_admin: {e}")
        return []

@method_decorator(login_required, name='dispatch')
class AdminPanelView(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            return redirect('login')
        try:
            # Obtener estadísticas
            total_estudiantes = Estudiante.objects.count()
            total_profesores = Docente.objects.count()
            total_asignaturas_impartidas = AsignaturaImpartida.objects.count()
            total_administradores = Administrativo.objects.count()
            total_clases = Clase.objects.count()
            total_asignaturas = Asignatura.objects.count()
            
            # Obtener todos los docentes con sus relaciones
            docentes = Docente.objects.select_related(
                'usuario',
                'especialidad'
            ).prefetch_related(
                'jefaturas'
            ).all()
            
            # Debug: imprimir información de los docentes
            print(f"Total de docentes encontrados: {len(docentes)}")
            for docente in docentes:
                print(f"Docente: {docente.usuario.nombre} {docente.usuario.apellido_paterno}")
                print(f"- ID: {docente.usuario.auth_user_id}")
                print(f"- Es profesor jefe: {docente.es_profesor_jefe}")
                print(f"- Tiene jefatura: {docente.jefaturas.exists()}")
            
            # Obtener todos los estudiantes
            estudiantes_sin_curso = Estudiante.objects.all().select_related('usuario', 'curso')
            
            # Obtener todos los usuarios ordenados por fecha de creación
            usuarios = Usuario.objects.all().order_by('-fecha_creacion')
            
            # Obtener todas las asignaturas con sus relaciones
            asignaturas = AsignaturaImpartida.objects.select_related(
                'asignatura',
                'docente__usuario'
            ).prefetch_related(
                'clases__curso'  # Agregamos la relación con curso
            ).distinct().all()

            # Mapeo de días en español
            DIAS_SEMANA = {
                'Monday': 'Lunes',
                'Tuesday': 'Martes',
                'Wednesday': 'Miércoles',
                'Thursday': 'Jueves',
                'Friday': 'Viernes',
                'Saturday': 'Sábado',
                'Sunday': 'Domingo'
            }

            # Mapeo de bloques a horarios
            BLOQUES_HORARIO = {
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

            def agrupar_bloques_consecutivos(bloques):
                if not bloques:
                    return []
                
                # Convertir bloques a números
                bloques_num = []
                for b in bloques:
                    for num, (inicio, fin) in BLOQUES_HORARIO.items():
                        if str(b) == num:
                            bloques_num.append(int(num))
                            break
                
                bloques_num.sort()
                grupos = []
                grupo_actual = [bloques_num[0]]

                for i in range(1, len(bloques_num)):
                    if bloques_num[i] == bloques_num[i-1] + 1:
                        grupo_actual.append(bloques_num[i])
                    else:
                        grupos.append(grupo_actual)
                        grupo_actual = [bloques_num[i]]
                grupos.append(grupo_actual)

                # Convertir grupos a rangos de horario
                rangos = []
                for grupo in grupos:
                    inicio = BLOQUES_HORARIO[str(grupo[0])][0]
                    fin = BLOQUES_HORARIO[str(grupo[-1])][1]
                    rangos.append(f"{inicio} - {fin}")

                return rangos

            # Procesar las asignaturas para evitar duplicados en cursos y bloques
            asignaturas_procesadas = []
            for asignatura in asignaturas:
                # Obtener cursos únicos
                cursos = set()
                for clase in asignatura.clases.all():
                    if clase.curso:
                        cursos.add((clase.curso.nivel, clase.curso.letra))
                
                # Si no hay cursos, marcar como electivo
                if not cursos:
                    cursos_texto = "Electivo"
                else:
                    # Ordenar los cursos
                    cursos_ordenados = sorted(list(cursos))
                    cursos_texto = ", ".join([
                        f"{nivel}°{letra}" 
                        for nivel, letra in cursos_ordenados
                    ])
                
                # Obtener bloques por día
                bloques_por_dia = {}
                for clase in asignatura.clases.all():
                    # Convertir la fecha a día de la semana
                    try:
                        if isinstance(clase.fecha, str):
                            from datetime import datetime
                            fecha_obj = datetime.strptime(clase.fecha, '%Y-%m-%d')
                            dia = DIAS_SEMANA[fecha_obj.strftime('%A')]
                        else:
                            dia = DIAS_SEMANA[clase.fecha.strftime('%A')]
                    except (ValueError, AttributeError, KeyError):
                        dia = str(clase.fecha)
                    
                    if dia not in bloques_por_dia:
                        bloques_por_dia[dia] = set()
                    bloques_por_dia[dia].add(clase.horario)
                
                # Crear un registro por cada día
                for dia, bloques in sorted(bloques_por_dia.items()):
                    registro = {
                        'codigo': asignatura.codigo,
                        'nombre': asignatura.asignatura.nombre,
                        'cursos': cursos_texto,
                        'dia': dia,
                        'horarios': agrupar_bloques_consecutivos(bloques)
                    }
                    asignaturas_procesadas.append(registro)

            # Obtener cursos con sus profesores jefe y estadísticas
            cursos = Curso.objects.select_related('jefatura_actual__docente__usuario').all()
            
            # Obtener todas las especialidades
            especialidades = Especialidad.objects.all()
            
            context = {
                'total_estudiantes': total_estudiantes,
                'total_profesores': total_profesores,
                'total_asignaturas_impartidas': total_asignaturas_impartidas,
                'total_administradores': total_administradores,
                'total_clases': total_clases,
                'total_asignaturas': total_asignaturas,
                'docentes': docentes,
                'estudiantes_sin_curso': estudiantes_sin_curso,
                'usuarios': usuarios,
                'asignaturas': asignaturas_procesadas,
                'cursos': cursos,
                'especialidades': especialidades,
            }
            return render(request, 'admin_panel.html', context)
        except Exception as e:
            messages.error(request, f'Error al cargar el panel de administrador: {str(e)}')
            return redirect('home')

    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, 'No tienes permiso para realizar esta acción')
            return redirect('login')

        try:
            action = request.POST.get('action')
            print("ok")
            if action == 'crear_curso':
                try:
                    # Validar datos
                    nivel = request.POST.get('nivel')
                    letra = request.POST.get('letra', '').upper()
                    profesor_jefe_id = request.POST.get('profesor_jefe_id')
                    
                    errores = []
                    if not nivel or not nivel.isdigit() or int(nivel) < 1 or int(nivel) > 4:
                        errores.append('El nivel debe estar entre 1 y 4')
                    
                    if not letra or letra not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
                        errores.append('La letra debe ser entre A e I')
                    
                    if not profesor_jefe_id:
                        errores.append('Debe seleccionar un profesor jefe')
                    
                    # Verificar si ya existe un curso con el mismo nivel y letra
                    if Curso.objects.filter(nivel=nivel, letra=letra).exists():
                        errores.append(f'Ya existe un curso {nivel}°{letra}')
                    
                    # Verificar si el profesor ya es jefe de otro curso
                    if profesor_jefe_id:
                        docente = get_object_or_404(Docente, usuario__auth_user_id=profesor_jefe_id)
                        if docente.jefaturas.filter(curso__isnull=False).exists():
                            errores.append('El profesor seleccionado ya es jefe de otro curso')
                    
                    if errores:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': False,
                                'errors': errores
                            })
                        for error in errores:
                            messages.error(request, error)
                        return redirect('admin_panel')
                    
                    with transaction.atomic():
                        # Crear el curso
                        curso = Curso.objects.create(
                            nivel=nivel,
                            letra=letra
                        )
                        
                        # Actualizar el docente y crear la relación de profesor jefe
                        docente = get_object_or_404(Docente, usuario__auth_user_id=profesor_jefe_id)
                        docente.es_profesor_jefe = True
                        docente.save()
                        
                        ProfesorJefe.objects.create(
                            docente=docente,
                            curso=curso
                        )
                        
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': True,
                                'message': f'Curso {curso.nivel}°{curso.letra} creado exitosamente'
                            })
                        
                        messages.success(request, f'Curso {curso.nivel}°{curso.letra} creado exitosamente')
                        return redirect('admin_panel')
                        
                except Exception as e:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': [str(e)]
                        })
                    messages.error(request, f'Error al crear curso: {str(e)}')
                    return redirect('admin_panel')
            
            elif action == 'crear_estudiante':
                data = {
                    'nombre': request.POST.get('nombre'),
                    'apellido_paterno': request.POST.get('apellido_paterno'),
                    'apellido_materno': request.POST.get('apellido_materno'),
                    'rut': request.POST.get('rut'),
                    'div': request.POST.get('div'),
                    'correo': request.POST.get('correo'),
                    'telefono': request.POST.get('telefono'),
                    'direccion': request.POST.get('direccion'),
                    'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                    'password': request.POST.get('password'),
                    'contacto_emergencia': request.POST.get('contacto_emergencia'),
                    'curso': request.POST.get('curso')
                }
                
                # Validar datos
                es_valido, errores = validadores.validar_data_crear_usuario(data, tipo_usuario='ESTUDIANTE')
                if not es_valido:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': errores
                        })
                    for error in errores:
                        messages.error(request, error)
                    return redirect('admin_panel')
                
                try:
                    usuario = crear_usuario(data, 'ESTUDIANTE')
                    messages.success(request, f'Estudiante {usuario.nombre} {usuario.apellido_paterno} creado exitosamente')
                except Exception as e:
                    messages.error(request, f'Error al crear estudiante: {str(e)}')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                return redirect('admin_panel')
                    
            elif action == 'crear_docente':
                data = {
                    'nombre': request.POST.get('nombre'),
                    'apellido_paterno': request.POST.get('apellido_paterno'),
                    'apellido_materno': request.POST.get('apellido_materno'),
                    'rut': request.POST.get('rut'),
                    'div': request.POST.get('div'),
                    'correo': request.POST.get('correo'),
                    'telefono': request.POST.get('telefono'),
                    'direccion': request.POST.get('direccion'),
                    'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                    'password': request.POST.get('password'),
                    'confirm_password': request.POST.get('confirm_password'),
                    'especialidad': request.POST.get('especialidad'),
                    'es_profesor_jefe': request.POST.get('es_profesor_jefe') == 'true'
                }
                
                # Validar datos
                es_valido, errores = validadores.validar_data_crear_usuario(data, tipo_usuario='DOCENTE')
                if not es_valido:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': {'__all__': errores}
                        })
                    for error in errores:
                        messages.error(request, error)
                    return redirect('admin_panel')
                
                try:
                    # Crear usuario base y docente
                    usuario = crear_usuario(data, 'DOCENTE')
                    messages.success(request, f'Docente {usuario.nombre} {usuario.apellido_paterno} creado exitosamente')
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    return redirect('admin_panel')
                    
                except Exception as e:
                    messages.error(request, f'Error al crear docente: {str(e)}')
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'errors': {'__all__': [str(e)]}})
                    return redirect('admin_panel')
                    
            elif action == 'crear_administrador':
                data = {
                    'nombre': request.POST.get('nombre'),
                    'apellido_paterno': request.POST.get('apellido_paterno'),
                    'apellido_materno': request.POST.get('apellido_materno'),
                    'rut': request.POST.get('rut'),
                    'div': request.POST.get('div'),
                    'correo': request.POST.get('correo'),
                    'telefono': request.POST.get('telefono'),
                    'direccion': request.POST.get('direccion'),
                    'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                    'password': request.POST.get('password'),
                    'confirm_password': request.POST.get('confirm_password'),
                    'tipo_usuario': 'ADMINISTRATIVO',
                    'rol': request.POST.get('rol', 'ADMINISTRATIVO')
                }
                
                # Validar datos
                es_valido, errores = validadores.validar_data_crear_usuario(data, tipo_usuario='ADMINISTRATIVO')
                if not es_valido:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': {'__all__': errores}
                        })
                    for error in errores:
                        messages.error(request, error)
                    return redirect('admin_panel')
                
                try:
                    # Crear usuario base y administrativo
                    usuario = crear_usuario(data, 'ADMINISTRATIVO')
                    messages.success(request, f'Administrador {usuario.nombre} {usuario.apellido_paterno} creado exitosamente')
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    return redirect('admin_panel')
                    
                except Exception as e:
                    messages.error(request, f'Error al crear administrador: {str(e)}')
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'errors': {'__all__': [str(e)]}})
                    return redirect('admin_panel')
                    
            elif action == 'crear_asignatura':
                try:
                    # Crear la asignatura base
                    asignatura = Asignatura.objects.create(
                        nombre=request.POST.get('nombre'),
                        nivel=request.POST.get('nivel'),
                        es_electivo=request.POST.get('es_electivo') == 'on'
                    )

                    # Crear la asignatura impartida
                    codigo = f"{asignatura.nombre[:3].upper()}{asignatura.nivel}"
                    asignatura_impartida = AsignaturaImpartida.objects.create(
                        asignatura=asignatura,
                        docente_id=request.POST.get('docente'),
                        codigo=codigo
                    )

                    # Crear la clase con el día, bloque y sala seleccionados
                    Clase.objects.create(
                        asignatura_impartida=asignatura_impartida,
                        fecha=request.POST.get('dia'),
                        bloque=request.POST.get('bloque'),
                        sala=request.POST.get('sala')
                    )

                    messages.success(request, 'Asignatura creada exitosamente')
                    return redirect('admin_panel')
                except Exception as e:
                    messages.error(request, f'Error al crear asignatura: {str(e)}')
                    return redirect('admin_panel')
            else:
                messages.error(request, 'Acción no válida')
                return redirect('admin_panel')
                
        except Exception as e:
            messages.error(request, f'Error al procesar la solicitud: {str(e)}')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            return redirect('admin_panel')

@method_decorator(login_required, name='dispatch')
class CreateAdminView(View):
    template_name = 'auth/create_admin.html'

    def get(self, request):
        if not request.user.is_admin:
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        return render(request, self.template_name)

    def post(self, request):
        if not request.user.is_admin:
            messages.error(request, 'No tienes permiso para realizar esta acción')
            return redirect('home')

        try:
            # Obtener datos del formulario
            data = {
                'nombre': request.POST.get('nombre'),
                'apellido_paterno': request.POST.get('apellido_paterno'),
                'apellido_materno': request.POST.get('apellido_materno'),
                'rut': request.POST.get('rut'),
                'div': request.POST.get('div'),
                'correo': request.POST.get('correo'),
                'telefono': request.POST.get('telefono'),
                'direccion': request.POST.get('direccion'),
                'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                'password': request.POST.get('password'),
                'confirm_password': request.POST.get('confirm_password'),
                'tipo_usuario': 'ADMINISTRATIVO',
                'rol_administrativo': request.POST.get('rol', 'ADMINISTRATIVO')
            }

            # Validar datos
            es_valido, errores = validadores.validar_data_crear_usuario(data)
            if not es_valido:
                for error in errores:
                    messages.error(request, error)
                return render(request, self.template_name)

            crear_usuario(data, 'ADMINISTRATIVO')
            messages.success(request, 'Administrador creado exitosamente')
            return redirect('user_list')

        except Exception as e:
            messages.error(request, f'Error al crear administrador: {str(e)}')
            return render(request, self.template_name)

@method_decorator(csrf_exempt, name='dispatch')
class ToggleUserStatusView(View):
    def post(self, request, user_id):
        try:
            # Verificar si el usuario está autenticado
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'error': 'Usuario no autenticado'})
            
            # Verificar si el usuario es administrador
            if not hasattr(request.user, 'is_admin') or not request.user.is_admin:
                return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'})
            
            usuario = get_object_or_404(Usuario, auth_user_id=user_id)
            
            # No permitir desactivar administradores máximos
            if hasattr(usuario, 'administrativo') and usuario.administrativo.rol == 'ADMINISTRADOR_MAXIMO':
                return JsonResponse({'success': False, 'error': 'No se puede desactivar un administrador máximo'})
            
            # Invertir el estado actual
            usuario.activador = not usuario.activador
            usuario.save()
            
            # También actualizar el estado en AuthUser
            auth_user = usuario.auth_user
            auth_user.is_active = usuario.activador
            auth_user.save()
            
            return JsonResponse({
                'success': True,
                'is_active': usuario.activador
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
class AdminPanelModularView(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            return redirect('login')
        try:
            # Obtener estadísticas
            total_estudiantes = Estudiante.objects.count()
            total_profesores = Docente.objects.count()
            total_asignaturas_impartidas = AsignaturaImpartida.objects.count()
            total_administradores = Administrativo.objects.count()
            total_clases = Clase.objects.count()
            total_asignaturas = Asignatura.objects.count()
            total_cursos = Curso.objects.count()
            
            # Calcular estadísticas adicionales para el panel modular
            cursos_con_jefe = Curso.objects.filter(jefatura_actual__isnull=False).count()
            cursos_sin_jefe = total_cursos - cursos_con_jefe
            promedio_estudiantes = round(total_estudiantes / total_cursos) if total_cursos > 0 else 0
            asignaturas_sin_profesor = AsignaturaImpartida.objects.filter(docente__isnull=True).count()
            
            # Los estudiantes se obtienen directamente desde la variable usuarios en el template
            
            # Obtener todos los docentes con sus relaciones
            docentes = Docente.objects.select_related(
                'usuario',
                'especialidad'
            ).prefetch_related(
                'jefaturas'
            ).all()
            
            # Obtener todos los estudiantes
            estudiantes_sin_curso = Estudiante.objects.all().select_related('usuario', 'curso')
            
            # Obtener todos los usuarios con sus relaciones (estudiante, docente, administrativo) y cursos
            usuarios = Usuario.objects.select_related(
                'estudiante__curso',
                'docente__especialidad', 
                'administrativo'
            ).order_by('-fecha_creacion')
            
            # Obtener todas las asignaturas con sus relaciones
            asignaturas = AsignaturaImpartida.objects.select_related(
                'asignatura',
                'docente__usuario'
            ).prefetch_related(
                'clases__curso'  # Agregamos la relación con curso
            ).distinct().all()

            # Mapeo de días en español
            DIAS_SEMANA = {
                'Monday': 'Lunes',
                'Tuesday': 'Martes',
                'Wednesday': 'Miércoles',
                'Thursday': 'Jueves',
                'Friday': 'Viernes',
                'Saturday': 'Sábado',
                'Sunday': 'Domingo'
            }

            # Mapeo de bloques a horarios
            BLOQUES_HORARIO = {
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

            def agrupar_bloques_consecutivos(bloques):
                if not bloques:
                    return []
                
                # Convertir bloques a números
                bloques_num = []
                for b in bloques:
                    for num, (inicio, fin) in BLOQUES_HORARIO.items():
                        if str(b) == num:
                            bloques_num.append(int(num))
                            break
                
                bloques_num.sort()
                grupos = []
                grupo_actual = [bloques_num[0]]

                for i in range(1, len(bloques_num)):
                    if bloques_num[i] == bloques_num[i-1] + 1:
                        grupo_actual.append(bloques_num[i])
                    else:
                        grupos.append(grupo_actual)
                        grupo_actual = [bloques_num[i]]
                grupos.append(grupo_actual)

                # Convertir grupos a rangos de horario
                rangos = []
                for grupo in grupos:
                    inicio = BLOQUES_HORARIO[str(grupo[0])][0]
                    fin = BLOQUES_HORARIO[str(grupo[-1])][1]
                    rangos.append(f"{inicio} - {fin}")

                return rangos

            # Procesar las asignaturas para evitar duplicados en cursos y bloques
            asignaturas_procesadas = []
            for asignatura in asignaturas:
                # Obtener cursos únicos
                cursos = set()
                for clase in asignatura.clases.all():
                    if clase.curso:
                        cursos.add((clase.curso.nivel, clase.curso.letra))
                
                # Si no hay cursos, marcar como electivo
                if not cursos:
                    cursos_texto = "Electivo"
                else:
                    # Ordenar los cursos
                    cursos_ordenados = sorted(list(cursos))
                    cursos_texto = ", ".join([
                        f"{nivel}°{letra}" 
                        for nivel, letra in cursos_ordenados
                    ])
                
                # Obtener bloques por día
                bloques_por_dia = {}
                for clase in asignatura.clases.all():
                    # Convertir la fecha a día de la semana
                    try:
                        if isinstance(clase.fecha, str):
                            from datetime import datetime
                            fecha_obj = datetime.strptime(clase.fecha, '%Y-%m-%d')
                            dia = DIAS_SEMANA[fecha_obj.strftime('%A')]
                        else:
                            dia = DIAS_SEMANA[clase.fecha.strftime('%A')]
                    except (ValueError, AttributeError, KeyError):
                        dia = str(clase.fecha)
                    
                    if dia not in bloques_por_dia:
                        bloques_por_dia[dia] = set()
                    bloques_por_dia[dia].add(clase.horario)
                
                # Crear un registro por cada día
                for dia, bloques in sorted(bloques_por_dia.items()):
                    registro = {
                        'codigo': asignatura.codigo,
                        'nombre': asignatura.asignatura.nombre,
                        'cursos': cursos_texto,
                        'dia': dia,
                        'horarios': agrupar_bloques_consecutivos(bloques)
                    }
                    asignaturas_procesadas.append(registro)

            # Obtener cursos con sus profesores jefe y estadísticas
            cursos = Curso.objects.select_related('jefatura_actual__docente__usuario').all()
            
            # Agregar estadísticas a cada curso
            for curso in cursos:
                curso.total_estudiantes = Estudiante.objects.filter(curso=curso).count()
                curso.total_asignaturas = AsignaturaImpartida.objects.filter(clases__curso=curso).distinct().count()
                
                # Calcular rendimiento académico del curso
                # Obtener todas las evaluaciones del curso
                evaluaciones_curso = Evaluacion.objects.filter(
                    clase__curso=curso
                ).distinct()
                
                # Calcular estadísticas de rendimiento
                if evaluaciones_curso.exists():
                    # Obtener notas de estudiantes del curso
                    notas_curso = AlumnoEvaluacion.objects.filter(
                        evaluacion__in=evaluaciones_curso,
                        estudiante__curso=curso
                    ).exclude(nota__isnull=True)
                    
                    if notas_curso.exists():
                        # Promedio general del curso
                        curso.promedio_general = round(notas_curso.aggregate(Avg('nota'))['nota__avg'] or 0, 2)
                        
                        # Calcular promedio por estudiante para clasificar correctamente
                        estudiantes_promedios = []
                        estudiantes_curso = Estudiante.objects.filter(curso=curso)
                        
                        for estudiante in estudiantes_curso:
                            notas_estudiante = notas_curso.filter(estudiante=estudiante)
                            if notas_estudiante.exists():
                                promedio_estudiante = notas_estudiante.aggregate(Avg('nota'))['nota__avg'] or 0
                                estudiantes_promedios.append(promedio_estudiante)
                        
                        # Contar estudiantes por estado de rendimiento basado en su promedio individual
                        curso.estudiantes_excelente = sum(1 for p in estudiantes_promedios if p >= 5.5)
                        curso.estudiantes_bueno = sum(1 for p in estudiantes_promedios if 4.5 <= p < 5.5)
                        curso.estudiantes_regular = sum(1 for p in estudiantes_promedios if 4.0 <= p < 4.5)
                        curso.estudiantes_deficiente = sum(1 for p in estudiantes_promedios if p < 4.0)
                        
                        # Calcular porcentaje de aprobación
                        aprobados = curso.estudiantes_excelente + curso.estudiantes_bueno
                        if curso.total_estudiantes > 0:
                            curso.porcentaje_aprobacion = round((aprobados * 100) / curso.total_estudiantes, 1)
                        else:
                            curso.porcentaje_aprobacion = 0
                        
                        # Total de evaluaciones realizadas
                        curso.total_evaluaciones = evaluaciones_curso.count()
                        
                        # Asignaturas con evaluaciones
                        curso.asignaturas_con_evaluaciones = evaluaciones_curso.values('evaluacion_base__asignatura').distinct().count()
                    else:
                        curso.promedio_general = 0
                        curso.estudiantes_excelente = 0
                        curso.estudiantes_bueno = 0
                        curso.estudiantes_regular = 0
                        curso.estudiantes_deficiente = 0
                        curso.porcentaje_aprobacion = 0
                        curso.total_evaluaciones = 0
                        curso.asignaturas_con_evaluaciones = 0
                else:
                    curso.promedio_general = 0
                    curso.estudiantes_excelente = 0
                    curso.estudiantes_bueno = 0
                    curso.estudiantes_regular = 0
                    curso.estudiantes_deficiente = 0
                    curso.porcentaje_aprobacion = 0
                    curso.total_evaluaciones = 0
                    curso.asignaturas_con_evaluaciones = 0
            
            # Obtener todas las especialidades
            especialidades = Especialidad.objects.all()
            
            # Obtener eventos del calendario para el administrador
            eventos_calendario_lista = get_eventos_calendario_admin()
            eventos_calendario = json.dumps(eventos_calendario_lista)  # Para el JavaScript
            
            # Obtener datos de comunicaciones
            comunicaciones = Comunicacion.objects.select_related('autor').prefetch_related('destinatarios_cursos', 'adjuntos').order_by('-fecha_envio')
            
            # Estadísticas de comunicaciones
            total_comunicaciones = comunicaciones.count()
            comunicaciones_con_adjuntos = comunicaciones.filter(adjuntos__isnull=False).distinct().count()
            comunicaciones_con_cursos = comunicaciones.filter(destinatarios_cursos__isnull=False).distinct().count()
            
            comunicaciones_stats = {
                'total': total_comunicaciones,
                'leidas': 0,  # Por ahora no tenemos sistema de lectura
                'no_leidas': total_comunicaciones,
                'con_adjuntos': comunicaciones_con_adjuntos,
                'con_cursos': comunicaciones_con_cursos,
                'porcentaje_leidas': 0
            }
            
            context = {
                'total_estudiantes': total_estudiantes,
                'total_profesores': total_profesores,
                'total_asignaturas_impartidas': total_asignaturas_impartidas,
                'total_administradores': total_administradores,
                'total_clases': total_clases,
                'total_asignaturas': total_asignaturas,
                'total_cursos': total_cursos,
                'cursos_con_jefe': cursos_con_jefe,
                'cursos_sin_jefe': cursos_sin_jefe,
                'promedio_estudiantes': promedio_estudiantes,
                'asignaturas_sin_profesor': asignaturas_sin_profesor,
                'docentes': docentes,
                'estudiantes_sin_curso': estudiantes_sin_curso,

                'usuarios': usuarios,
                'asignaturas': asignaturas_procesadas,  # Usamos la lista procesada
                'cursos': cursos,
                'especialidades': especialidades,
                'eventos_calendario': eventos_calendario,
                'comunicaciones': comunicaciones,
                'comunicaciones_stats': comunicaciones_stats,
            }
            return render(request, 'admin_panel_modular.html', context)
        except Exception as e:
            messages.error(request, f'Error al cargar el panel de administrador modular: {str(e)}')
            return redirect('home')

    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, 'No tienes permiso para realizar esta acción')
            return redirect('login')

        try:
            action = request.POST.get('action')
            
            if action == 'crear_curso':
                try:
                    # Validar datos
                    nivel = request.POST.get('nivel')
                    letra = request.POST.get('letra', '').upper()
                    profesor_jefe_id = request.POST.get('profesor_jefe_id')
                    
                    errores = []
                    if not nivel or not nivel.isdigit() or int(nivel) < 1 or int(nivel) > 4:
                        errores.append('El nivel debe estar entre 1 y 4')
                    
                    if not letra or letra not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
                        errores.append('La letra debe ser entre A e I')
                    
                    if not profesor_jefe_id:
                        errores.append('Debe seleccionar un profesor jefe')
                    
                    # Verificar si ya existe un curso con el mismo nivel y letra
                    if Curso.objects.filter(nivel=nivel, letra=letra).exists():
                        errores.append(f'Ya existe un curso {nivel}°{letra}')
                    
                    # Verificar si el profesor ya es jefe de otro curso
                    if profesor_jefe_id:
                        docente = get_object_or_404(Docente, usuario__auth_user_id=profesor_jefe_id)
                        if docente.jefaturas.filter(curso__isnull=False).exists():
                            errores.append('El profesor seleccionado ya es jefe de otro curso')
                    
                    if errores:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': False,
                                'errors': errores
                            })
                        for error in errores:
                            messages.error(request, error)
                        return redirect('admin_panel')
                    
                    with transaction.atomic():
                        # Crear el curso
                        curso = Curso.objects.create(
                            nivel=nivel,
                            letra=letra
                        )
                        
                        # Actualizar el docente y crear la relación de profesor jefe
                        docente = get_object_or_404(Docente, usuario__auth_user_id=profesor_jefe_id)
                        docente.es_profesor_jefe = True
                        docente.save()
                        
                        ProfesorJefe.objects.create(
                            docente=docente,
                            curso=curso
                        )
                        
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': True,
                                'message': f'Curso {curso.nivel}°{curso.letra} creado exitosamente'
                            })
                        
                        messages.success(request, f'Curso {curso.nivel}°{curso.letra} creado exitosamente')
                        return redirect('admin_panel')
                        
                except Exception as e:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': [str(e)]
                        })
                    messages.error(request, f'Error al crear curso: {str(e)}')
                    return redirect('admin_panel')
            
            elif action == 'crear_estudiante':
                data = {
                    'nombre': request.POST.get('nombre'),
                    'apellido_paterno': request.POST.get('apellido_paterno'),
                    'apellido_materno': request.POST.get('apellido_materno'),
                    'rut': request.POST.get('rut'),
                    'div': request.POST.get('div'),
                    'correo': request.POST.get('correo'),
                    'telefono': request.POST.get('telefono'),
                    'direccion': request.POST.get('direccion'),
                    'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                    'password': request.POST.get('password'),
                    'contacto_emergencia': request.POST.get('contacto_emergencia'),
                    'curso': request.POST.get('curso')
                }
                
                # Validar datos
                es_valido, errores = validadores.validar_data_crear_usuario(data, tipo_usuario='ESTUDIANTE')
                if not es_valido:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': errores
                        })
                    for error in errores:
                        messages.error(request, error)
                    return redirect('admin_panel')
                
                try:
                    usuario = crear_usuario(data, 'ESTUDIANTE')
                    messages.success(request, f'Estudiante {usuario.nombre} {usuario.apellido_paterno} creado exitosamente')
                except Exception as e:
                    messages.error(request, f'Error al crear estudiante: {str(e)}')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                return redirect('admin_panel')
            
            elif action == 'crear_docente':
                data = {
                    'nombre': request.POST.get('nombre'),
                    'apellido_paterno': request.POST.get('apellido_paterno'),
                    'apellido_materno': request.POST.get('apellido_materno'),
                    'rut': request.POST.get('rut'),
                    'div': request.POST.get('div'),
                    'correo': request.POST.get('correo'),
                    'telefono': request.POST.get('telefono'),
                    'direccion': request.POST.get('direccion'),
                    'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                    'password': request.POST.get('password'),
                    'especialidad': request.POST.get('especialidad')
                }
                
                # Validar datos
                es_valido, errores = validadores.validar_data_crear_usuario(data, tipo_usuario='DOCENTE')
                if not es_valido:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': errores
                        })
                    for error in errores:
                        messages.error(request, error)
                    return redirect('admin_panel')
                
                try:
                    usuario = crear_usuario(data, 'DOCENTE')
                    messages.success(request, f'Docente {usuario.nombre} {usuario.apellido_paterno} creado exitosamente')
                except Exception as e:
                    messages.error(request, f'Error al crear docente: {str(e)}')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                return redirect('admin_panel')
            
            elif action == 'crear_administrador':
                data = {
                    'nombre': request.POST.get('nombre'),
                    'apellido_paterno': request.POST.get('apellido_paterno'),
                    'apellido_materno': request.POST.get('apellido_materno'),
                    'rut': request.POST.get('rut'),
                    'div': request.POST.get('div'),
                    'correo': request.POST.get('correo'),
                    'telefono': request.POST.get('telefono'),
                    'direccion': request.POST.get('direccion'),
                    'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                    'password': request.POST.get('password'),
                    'rol': request.POST.get('rol')
                }
                
                # Validar datos
                es_valido, errores = validadores.validar_data_crear_usuario(data, tipo_usuario='ADMINISTRATIVO')
                if not es_valido:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': errores
                        })
                    for error in errores:
                        messages.error(request, error)
                    return redirect('admin_panel')
                
                try:
                    usuario = crear_usuario(data, 'ADMINISTRATIVO')
                    messages.success(request, f'Administrador {usuario.nombre} {usuario.apellido_paterno} creado exitosamente')
                except Exception as e:
                    messages.error(request, f'Error al crear administrador: {str(e)}')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                return redirect('admin_panel')
            
            elif action == 'crear_asignatura':
                try:
                    codigo = request.POST.get('codigo')
                    nombre = request.POST.get('nombre')
                    nivel = request.POST.get('nivel')
                    profesor_id = request.POST.get('profesor')
                    es_electivo = request.POST.get('es_electivo') == 'on'
                    
                    errores = []
                    if not codigo:
                        errores.append('El código es obligatorio')
                    if not nombre:
                        errores.append('El nombre es obligatorio')
                    if not nivel:
                        errores.append('Debe seleccionar un nivel')
                    
                    # Verificar si ya existe una asignatura impartida con el mismo código
                    if AsignaturaImpartida.objects.filter(codigo=codigo).exists():
                        errores.append(f'Ya existe una asignatura con el código {codigo}')
                    
                    if errores:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': False,
                                'errors': errores
                            })
                        for error in errores:
                            messages.error(request, error)
                        return redirect('admin_panel')
                    
                    # Verificar si ya existe una asignatura con el mismo nombre y nivel
                    asignatura, created = Asignatura.objects.get_or_create(
                        nombre=nombre,
                        nivel=nivel,
                        defaults={'es_electivo': es_electivo}
                    )
                    
                    # Crear la asignatura impartida
                    docente = None
                    if profesor_id:
                        docente = get_object_or_404(Docente, usuario__auth_user_id=profesor_id)
                    
                    asignatura_impartida = AsignaturaImpartida.objects.create(
                        asignatura=asignatura,
                        docente=docente,
                        codigo=codigo
                    )
                    
                    # Si no es electiva, crear clases para todos los cursos del nivel
                    if not es_electivo:
                        cursos_nivel = Curso.objects.filter(nivel=nivel)
                        for curso in cursos_nivel:
                            # Crear al menos una clase de ejemplo (se puede personalizar después)
                            Clase.objects.create(
                                asignatura_impartida=asignatura_impartida,
                                curso=curso,
                                fecha='LUNES',  # Día por defecto
                                horario='1',    # Bloque por defecto
                                sala='SALA_1'   # Sala por defecto
                            )
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'message': f'Asignatura {asignatura.nombre} creada exitosamente'
                        })
                    
                    messages.success(request, f'Asignatura {asignatura.nombre} creada exitosamente')
                    return redirect('admin_panel')
                    
                except Exception as e:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': [str(e)]
                        })
                    messages.error(request, f'Error al crear asignatura: {str(e)}')
                    return redirect('admin_panel')
            
            else:
                messages.error(request, 'Acción no válida')
                return redirect('admin_panel')
                
        except Exception as e:
            messages.error(request, f'Error en el panel de administrador: {str(e)}')
            return redirect('admin_panel')

@method_decorator(login_required, name='dispatch')
class AdminEventosCalendarioView(View):
    """
    Vista AJAX para obtener eventos del calendario para el administrador
    """
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            return JsonResponse({'error': 'No autorizado'}, status=403)
        
        try:
            eventos = get_eventos_calendario_admin()
            return JsonResponse(eventos, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(login_required, name='dispatch')  
class AdminCrearEventoCalendarioView(View):
    """
    Vista para crear eventos desde el panel de administrador
    """
    def get(self, request):
        """Mostrar el formulario para crear un nuevo evento"""
        if not request.user.is_authenticated or not request.user.is_admin:
            return redirect('login')
        
        return render(request, 'calendario/crear_evento.html')
    
    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            return JsonResponse({'success': False, 'error': 'No autorizado'})
        
        try:
            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion')
            fecha = request.POST.get('fecha')
            hora = request.POST.get('hora')
            tipo_evento = request.POST.get('tipo')
            ubicacion = request.POST.get('ubicacion', '')
            encargado = request.POST.get('encargado', '')
            
            # Validaciones básicas
            if not titulo or not fecha or not tipo_evento:
                return JsonResponse({'success': False, 'error': 'Faltan campos obligatorios (título, fecha y tipo de evento)'})
            
            # Crear evento del colegio (institucional)
            evento = CalendarioColegio.objects.create(
                nombre_actividad=titulo,
                descripcion=descripcion or '',
                fecha=fecha,
                hora=hora or '00:00:00',
                ubicacion=ubicacion,
                encargado=encargado or f"Administrador ({request.user.rut})"
            )
            
            return JsonResponse({
                'success': True, 
                'message': 'Evento creado exitosamente',
                'evento_id': evento.id
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
class AdminEditarEventoCalendarioView(View):
    """
    Vista para editar eventos desde el panel de administrador
    """
    def get(self, request, evento_id):
        if not request.user.is_authenticated or not request.user.is_admin:
            # Si es petición AJAX, devolver JSON, sino redirigir
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'No autorizado'})
            return redirect('login')
        
        try:
            # Determinar si es evento de colegio o clase
            if evento_id.startswith('colegio_'):
                evento_id_real = evento_id.replace('colegio_', '')
                evento = get_object_or_404(CalendarioColegio, pk=evento_id_real)
                evento.tipo = 'Colegio'
                evento.titulo = evento.nombre_actividad
            elif evento_id.startswith('clase_'):
                evento_id_real = evento_id.replace('clase_', '')
                evento = get_object_or_404(CalendarioClase, pk=evento_id_real)
                evento.tipo = 'Asignatura'
                evento.titulo = f"{evento.nombre_actividad} - {evento.asignatura.nombre}"
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Evento no encontrado'})
                messages.error(request, 'Evento no encontrado')
                return redirect('admin_panel')
            
            # Agregar el ID original con prefijo
            evento.id_completo = evento_id
            
            # Si es petición AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                if evento.tipo == 'Colegio':
                    return JsonResponse({
                        'success': True,
                        'evento': {
                            'titulo': evento.nombre_actividad,
                            'descripcion': evento.descripcion,
                            'fecha': evento.fecha.strftime('%Y-%m-%d'),
                            'hora': str(evento.hora),
                            'ubicacion': evento.ubicacion,
                            'encargado': evento.encargado,
                            'tipo': 'colegio'
                        }
                    })
                else:  # Asignatura
                    return JsonResponse({
                        'success': True,
                        'evento': {
                            'titulo': evento.nombre_actividad,
                            'descripcion': evento.descripcion,
                            'fecha': evento.fecha.strftime('%Y-%m-%d'),
                            'hora': str(evento.hora) if evento.hora else '00:00:00',
                            'asignatura': evento.asignatura.nombre,
                            'tipo': 'clase'
                        }
                    })
            
            # Si es petición normal, devolver HTML
            context = {
                'evento': evento,
            }
            
            return render(request, 'calendario/editar_evento.html', context)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f'Error al cargar el evento: {str(e)}')
            return redirect('admin_panel')
    
    def post(self, request, evento_id):
        if not request.user.is_authenticated or not request.user.is_admin:
            return JsonResponse({'success': False, 'error': 'No autorizado'})
        
        try:
            event_type, id_numerico = evento_id.split('_', 1)
            
            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion')
            fecha = request.POST.get('fecha')
            hora = request.POST.get('hora')
            ubicacion = request.POST.get('ubicacion', '')
            encargado = request.POST.get('encargado', '')
            
            if event_type == 'colegio':
                evento = CalendarioColegio.objects.filter(id=id_numerico).first()
                if not evento:
                    return JsonResponse({'success': False, 'error': 'Evento no encontrado'})
                
                # Actualizar evento
                evento.nombre_actividad = titulo
                evento.descripcion = descripcion
                evento.fecha = fecha
                evento.hora = hora
                evento.ubicacion = ubicacion
                evento.encargado = encargado
                evento.save()
                
            elif event_type == 'clase':
                evento = CalendarioClase.objects.filter(id=id_numerico).first()
                if not evento:
                    return JsonResponse({'success': False, 'error': 'Evento no encontrado'})
                
                # Actualizar evento
                evento.nombre_actividad = titulo
                evento.descripcion = descripcion
                evento.fecha = fecha
                evento.hora = hora
                evento.save()
            
            return JsonResponse({'success': True, 'message': 'Evento actualizado exitosamente'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
class AdminDetalleEventoCalendarioView(View):
    """Vista para mostrar el detalle de un evento del calendario"""
    
    def get(self, request, evento_id):
        if not request.user.is_authenticated or not request.user.is_admin:
            return redirect('login')
        
        try:
            # Determinar si es evento de colegio o clase
            if evento_id.startswith('colegio_'):
                evento_id_real = evento_id.replace('colegio_', '')
                evento = get_object_or_404(CalendarioColegio, pk=evento_id_real)
                evento.tipo = 'Colegio'
                evento.titulo = evento.nombre_actividad
            elif evento_id.startswith('clase_'):
                evento_id_real = evento_id.replace('clase_', '')
                evento = get_object_or_404(CalendarioClase, pk=evento_id_real)
                evento.tipo = 'Asignatura'
                evento.titulo = f"{evento.nombre_actividad} - {evento.asignatura.nombre}"
                # Intentar obtener información del curso
                try:
                    from Core.models import AsignaturaImpartida, Clase
                    asignatura_impartida = AsignaturaImpartida.objects.filter(
                        asignatura=evento.asignatura
                    ).first()
                    
                    if asignatura_impartida:
                        clase = Clase.objects.filter(
                            asignatura_impartida=asignatura_impartida
                        ).first()
                        
                        if clase and clase.curso:
                            evento.curso = clase.curso
                except:
                    evento.curso = None
            else:
                messages.error(request, 'Evento no encontrado')
                return redirect('admin_panel')
            
            # Agregar el ID original con prefijo para los botones de acción
            evento.id_completo = evento_id
            
            context = {
                'evento': evento,
            }
            
            return render(request, 'calendario/detalle_evento.html', context)
            
        except Exception as e:
            messages.error(request, f'Error al cargar el detalle del evento: {str(e)}')
            return redirect('admin_panel')

@method_decorator(login_required, name='dispatch')
class AdminEliminarEventoCalendarioView(View):
    """
    Vista para eliminar eventos desde el panel de administrador
    """
    def post(self, request, evento_id):
        if not request.user.is_authenticated or not request.user.is_admin:
            return JsonResponse({'success': False, 'error': 'No autorizado'})
        
        try:
            event_type, id_numerico = evento_id.split('_', 1)
            
            if event_type == 'colegio':
                evento = CalendarioColegio.objects.filter(id=id_numerico).first()
                if not evento:
                    return JsonResponse({'success': False, 'error': 'Evento no encontrado'})
                
                titulo = evento.nombre_actividad
                evento.delete()
                
            elif event_type == 'clase':
                evento = CalendarioClase.objects.filter(id=id_numerico).first()
                if not evento:
                    return JsonResponse({'success': False, 'error': 'Evento no encontrado'})
                
                titulo = evento.nombre_actividad
                evento.delete()
            
            return JsonResponse({'success': True, 'message': f'Evento "{titulo}" eliminado exitosamente'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
class ApiCursosView(View):
    """API para obtener la lista de cursos"""
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'No autorizado'}, status=401)
        
        try:
            cursos = Curso.objects.all().order_by('nivel', 'letra')
            data = []
            for curso in cursos:
                data.append({
                    'id': curso.id,
                    'nombre': f"{curso.nivel}°{curso.letra}"
                })
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(login_required, name='dispatch')
class ApiAsignaturasView(View):
    """API para obtener la lista de asignaturas"""
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'No autorizado'}, status=401)
        
        try:
            asignaturas = Asignatura.objects.all().order_by('nombre')
            data = []
            for asignatura in asignaturas:
                data.append({
                    'id': asignatura.id,
                    'nombre': asignatura.nombre
                })
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator([login_required, csrf_exempt], name='dispatch')
class CursoDataView(View):
    """Vista para obtener datos de un curso específico"""
    def get(self, request, curso_id):
        if not request.user.is_admin:
            return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'})
        
        try:
            curso = get_object_or_404(Curso, id=curso_id)
            
            # Obtener profesor jefe de manera segura
            profesor_jefe = None
            try:
                if hasattr(curso, 'jefatura_actual') and curso.jefatura_actual:
                    profesor_jefe = {
                        'id': curso.jefatura_actual.docente.usuario.auth_user_id,
                        'nombre': curso.jefatura_actual.docente.usuario.get_full_name()
                    }
            except Exception:
                profesor_jefe = None
            
            # Obtener contadores
            try:
                total_estudiantes = Estudiante.objects.filter(curso=curso).count()
            except Exception:
                total_estudiantes = 0
                
            try:
                total_asignaturas = AsignaturaImpartida.objects.filter(clases__curso=curso).distinct().count()
            except Exception:
                total_asignaturas = 0
            
            # Devolver solo los datos básicos
            data = {
                'success': True,
                'id': curso.id,
                'nivel': curso.nivel,
                'letra': curso.letra,
                'nombre': f"{curso.nivel}°{curso.letra}",
                'total_estudiantes': total_estudiantes,
                'total_asignaturas': total_asignaturas,
                'profesor_jefe': profesor_jefe
            }
            
            return JsonResponse(data)
            
        except Curso.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'El curso no existe'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': 'Error al cargar los datos del curso'
            })

@method_decorator([login_required, csrf_exempt], name='dispatch')
class CursoUpdateView(View):
    """Vista para actualizar un curso"""
    def post(self, request, curso_id):
        try:
            if not request.user.is_admin:
                return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'})
            
            curso = get_object_or_404(Curso, id=curso_id)
            
            # Manejar tanto JSON como form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                nivel = data.get('nivel')
                letra = data.get('letra', '').upper()
                profesor_jefe_id = data.get('profesor_jefe_id')
            else:
                nivel = request.POST.get('nivel')
                letra = request.POST.get('letra', '').upper()
                profesor_jefe_id = request.POST.get('profesor_jefe_id')
            
            errores = []
            
            # Validar datos
            if not nivel or not nivel.isdigit() or int(nivel) < 1 or int(nivel) > 4:
                errores.append('El nivel debe estar entre 1 y 4')
            
            if not letra or letra not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
                errores.append('La letra debe ser entre A e I')
            
            # Verificar si ya existe otro curso con el mismo nivel y letra
            curso_existente = Curso.objects.filter(nivel=nivel, letra=letra).exclude(id=curso_id).first()
            if curso_existente:
                errores.append(f'Ya existe otro curso {nivel}°{letra}')
            
            if errores:
                return JsonResponse({'success': False, 'errors': errores})
            
            with transaction.atomic():
                # Actualizar datos del curso
                curso.nivel = int(nivel)
                curso.letra = letra
                curso.save()
                
                # Actualizar profesor jefe si se especifica
                if profesor_jefe_id:
                    # Quitar profesor jefe anterior si existe
                    if hasattr(curso, 'jefatura_actual') and curso.jefatura_actual:
                        profesor_anterior = curso.jefatura_actual.docente
                        curso.jefatura_actual.delete()
                        # Si el profesor anterior no tiene otras jefaturas, desmarcar es_profesor_jefe
                        if not profesor_anterior.jefaturas.exists():
                            profesor_anterior.es_profesor_jefe = False
                            profesor_anterior.save()
                    
                    # Asignar nuevo profesor jefe
                    docente = get_object_or_404(Docente, usuario__auth_user_id=profesor_jefe_id)
                    
                    # Verificar si el docente ya es jefe de otro curso
                    if docente.jefaturas.filter(curso__isnull=False).exclude(curso=curso).exists():
                        return JsonResponse({
                            'success': False, 
                            'errors': ['El profesor seleccionado ya es jefe de otro curso']
                        })
                    
                    docente.es_profesor_jefe = True
                    docente.save()
                    
                    ProfesorJefe.objects.create(
                        docente=docente,
                        curso=curso
                    )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Curso {curso.nivel}°{curso.letra} actualizado exitosamente'
                })
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator([login_required, csrf_exempt], name='dispatch')
class CursoDeleteView(View):
    """Vista para eliminar un curso"""
    def post(self, request, curso_id):
        try:
            if not request.user.is_admin:
                return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'})
            
            curso = get_object_or_404(Curso, id=curso_id)
            
            # Verificar si el curso tiene estudiantes asignados
            total_estudiantes = Estudiante.objects.filter(curso=curso).count()
            if total_estudiantes > 0:
                return JsonResponse({
                    'success': False,
                    'error': f'No se puede eliminar el curso {curso.nivel}°{curso.letra} porque tiene {total_estudiantes} estudiantes asignados'
                })
            
            # Verificar si el curso tiene asignaturas asignadas
            total_asignaturas = AsignaturaImpartida.objects.filter(clases__curso=curso).count()
            if total_asignaturas > 0:
                return JsonResponse({
                    'success': False,
                    'error': f'No se puede eliminar el curso {curso.nivel}°{curso.letra} porque tiene {total_asignaturas} asignaturas asignadas'
                })
            
            # Verificar si el curso tiene comunicaciones
            total_comunicaciones = curso.comunicaciones.count()
            if total_comunicaciones > 0:
                return JsonResponse({
                    'success': False,
                    'error': f'No se puede eliminar el curso {curso.nivel}°{curso.letra} porque tiene {total_comunicaciones} comunicaciones asociadas'
                })
            
            # Verificar si el curso tiene anotaciones
            total_anotaciones = curso.anotaciones.count()
            if total_anotaciones > 0:
                return JsonResponse({
                    'success': False,
                    'error': f'No se puede eliminar el curso {curso.nivel}°{curso.letra} porque tiene {total_anotaciones} anotaciones asociadas'
                })
            
            with transaction.atomic():
                curso_nombre = f"{curso.nivel}°{curso.letra}"
                
                # Eliminar jefatura si existe
                if hasattr(curso, 'jefatura_actual') and curso.jefatura_actual:
                    profesor_jefe = curso.jefatura_actual.docente
                    curso.jefatura_actual.delete()
                    # Si el profesor no tiene otras jefaturas, desmarcar es_profesor_jefe
                    if not profesor_jefe.jefaturas.exists():
                        profesor_jefe.es_profesor_jefe = False
                        profesor_jefe.save()
                
                # Eliminar el curso
                curso.delete()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Curso {curso_nombre} eliminado exitosamente'
                })
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator([login_required, csrf_exempt], name='dispatch')
class AsignaturaDataView(View):
    """Vista para obtener datos de una asignatura específica"""
    def get(self, request, asignatura_id):
        try:
            if not request.user.is_admin:
                return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'})
            
            asignatura = get_object_or_404(Asignatura, id=asignatura_id)
            
            # Obtener imparticiones
            imparticiones = []
            for imparticion in asignatura.imparticiones.all().select_related('docente__usuario'):
                imparticiones.append({
                    'id': imparticion.id,
                    'codigo': imparticion.codigo,
                    'docente': imparticion.docente.usuario.get_full_name() if imparticion.docente else 'Sin docente'
                })
            
            # Obtener objetivos
            objetivos = []
            for objetivo in asignatura.objetivos.all():
                objetivos.append({
                    'id': objetivo.id,
                    'descripcion': objetivo.descripcion,
                    'completado': objetivo.completado
                })
            
            # Obtener recursos
            recursos = []
            for recurso in asignatura.recursos.all():
                recursos.append({
                    'id': recurso.id,
                    'titulo': recurso.titulo,
                    'tipo': recurso.get_tipo_display(),
                    'descripcion': recurso.descripcion
                })
            
            # Obtener evaluaciones base
            evaluaciones = []
            for evaluacion in asignatura.evaluaciones_base.all():
                evaluaciones.append({
                    'id': evaluacion.id,
                    'nombre': evaluacion.nombre,
                    'descripcion': evaluacion.descripcion,
                    'ponderacion': float(evaluacion.ponderacion)
                })
            
            data = {
                'id': asignatura.id,
                'nombre': asignatura.nombre,
                'nivel': asignatura.nivel,
                'es_electivo': asignatura.es_electivo,
                'imparticiones': imparticiones,
                'objetivos': objetivos,
                'recursos': recursos,
                'evaluaciones': evaluaciones
            }
            
            return JsonResponse({'success': True, 'data': data})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator([login_required, csrf_exempt], name='dispatch')
class AsignaturaUpdateView(View):
    """Vista para actualizar una asignatura"""
    def post(self, request, asignatura_id):
        try:
            if not request.user.is_admin:
                return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'})
            
            asignatura = get_object_or_404(Asignatura, id=asignatura_id)
            
            data = json.loads(request.body)
            nombre = data.get('nombre')
            nivel = data.get('nivel')
            es_electivo = data.get('es_electivo', False)
            
            errores = []
            
            # Validar datos
            if not nombre:
                errores.append('El nombre es requerido')
            
            if not nivel or not str(nivel).isdigit() or int(nivel) < 1 or int(nivel) > 4:
                errores.append('El nivel debe estar entre 1 y 4')
            
            if errores:
                return JsonResponse({'success': False, 'errors': errores})
            
            # Actualizar datos de la asignatura
            asignatura.nombre = nombre
            asignatura.nivel = int(nivel)
            asignatura.es_electivo = es_electivo
            asignatura.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Asignatura {asignatura.nombre} actualizada exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator([login_required, csrf_exempt], name='dispatch')
class AsignaturaDeleteView(View):
    """Vista para eliminar una asignatura"""
    def post(self, request, asignatura_id):
        try:
            if not request.user.is_admin:
                return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'})
            
            asignatura = get_object_or_404(Asignatura, id=asignatura_id)
            
            # Verificar si la asignatura tiene imparticiones
            total_imparticiones = asignatura.imparticiones.count()
            if total_imparticiones > 0:
                return JsonResponse({
                    'success': False,
                    'error': f'No se puede eliminar la asignatura {asignatura.nombre} porque tiene {total_imparticiones} imparticiones'
                })
            
            # Verificar si la asignatura tiene objetivos
            total_objetivos = asignatura.objetivos.count()
            if total_objetivos > 0:
                return JsonResponse({
                    'success': False,
                    'error': f'No se puede eliminar la asignatura {asignatura.nombre} porque tiene {total_objetivos} objetivos'
                })
            
            # Verificar si la asignatura tiene recursos
            total_recursos = asignatura.recursos.count()
            if total_recursos > 0:
                return JsonResponse({
                    'success': False,
                    'error': f'No se puede eliminar la asignatura {asignatura.nombre} porque tiene {total_recursos} recursos'
                })
            
            # Verificar si la asignatura tiene evaluaciones base
            total_evaluaciones = asignatura.evaluaciones_base.count()
            if total_evaluaciones > 0:
                return JsonResponse({
                    'success': False,
                    'error': f'No se puede eliminar la asignatura {asignatura.nombre} porque tiene {total_evaluaciones} evaluaciones base'
                })
            
            # Eliminar la asignatura
            asignatura_nombre = asignatura.nombre
            asignatura.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Asignatura {asignatura_nombre} eliminada exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator([login_required, csrf_exempt], name='dispatch')
class AsignaturaCreateView(View):
    """Vista para crear una asignatura"""
    def post(self, request):
        try:
            if not request.user.is_admin:
                return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'})
            
            data = json.loads(request.body)
            nombre = data.get('nombre')
            nivel = data.get('nivel')
            es_electivo = data.get('es_electivo', False)
            
            errores = []
            
            # Validar datos
            if not nombre:
                errores.append('El nombre es requerido')
            
            if not nivel or not str(nivel).isdigit() or int(nivel) < 1 or int(nivel) > 4:
                errores.append('El nivel debe estar entre 1 y 4')
            
            # Verificar si ya existe una asignatura con el mismo nombre y nivel
            if Asignatura.objects.filter(nombre=nombre, nivel=nivel).exists():
                errores.append(f'Ya existe una asignatura con el nombre {nombre} en el nivel {nivel}°')
            
            if errores:
                return JsonResponse({'success': False, 'errors': errores})
            
            # Crear la asignatura
            asignatura = Asignatura.objects.create(
                nombre=nombre,
                nivel=int(nivel),
                es_electivo=es_electivo
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Asignatura {asignatura.nombre} creada exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
