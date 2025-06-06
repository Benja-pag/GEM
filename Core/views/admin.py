from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from Core.models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura, AsignaturaImpartida, Curso, ProfesorJefe, Especialidad
from django.db.models import Count, Avg
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from Core.servicios.repos import usuarios
from Core.servicios.helpers import validadores, serializadores
from Core.servicios.repos.usuarios import crear_usuario, actualizar_usuario
from Core.servicios.repos.cursos import get_curso, get_estudiantes_por_curso
from django.http import JsonResponse

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
            
            # Obtener todos los docentes para el formulario de creación de curso
            docentes = Docente.objects.select_related('usuario').all()
            
            # Obtener todos los estudiantes
            estudiantes_sin_curso = Estudiante.objects.all().select_related('usuario', 'curso')
            
            # Obtener todos los usuarios ordenados por fecha de creación
            usuarios = Usuario.objects.all().order_by('-fecha_creacion')
            
            # Obtener todas las asignaturas con sus relaciones
            asignaturas = AsignaturaImpartida.objects.select_related(
                'asignatura',
                'docente__usuario'
            ).prefetch_related('clases').all()
            
            # Obtener cursos con sus profesores jefe
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
                'asignaturas': asignaturas,
                'cursos': cursos,
                'especialidades': especialidades,
            }
            return render(request, 'admin_panel.html', context)
        except Exception as e:
            messages.error(request, f'Error al cargar el panel de administrador: {str(e)}')
            return redirect('home')

    def post(self, request):
        if not request.user.is_admin:
            messages.error(request, 'No tienes permiso para realizar esta acción')
            return redirect('home')
        
        action = request.POST.get('action')
        
        try:
            if action == 'crear_estudiante':
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
                    
            elif action == 'crear_curso':
                try:
                    # Obtener los datos del formulario
                    nivel = request.POST.get('nivel')
                    letra = request.POST.get('letra').upper()  # Convertir a mayúscula
                    profesor_jefe_id = request.POST.get('profesor_jefe_id')

                    # Validar que todos los campos requeridos estén presentes
                    errores = []
                    if not nivel:
                        errores.append('El nivel es obligatorio')
                    if not letra:
                        errores.append('La letra es obligatoria')
                    if not profesor_jefe_id:
                        errores.append('El profesor jefe es obligatorio')

                    # Validar formato de nivel
                    try:
                        nivel = int(nivel)
                        if nivel < 1 or nivel > 12:
                            errores.append('El nivel debe estar entre 1 y 12')
                    except ValueError:
                        errores.append('El nivel debe ser un número válido')

                    # Validar formato de letra
                    if letra and not letra.isalpha():
                        errores.append('La letra debe ser un carácter alfabético')

                    if errores:
                        return JsonResponse({
                            'success': False,
                            'errors': {'__all__': errores}
                        })

                    # Verificar si ya existe un curso con el mismo nivel y letra
                    curso_existente = Curso.objects.filter(nivel=nivel, letra=letra).first()
                    if curso_existente:
                        return JsonResponse({
                            'success': False,
                            'errors': {'__all__': [f'Ya existe un curso {nivel}°{letra}. Por favor, elija otro nivel o letra.']}
                        })

                    # Verificar si el profesor ya es jefe de otro curso
                    profesor_jefe = Docente.objects.get(usuario_id=profesor_jefe_id)
                    jefatura_existente = ProfesorJefe.objects.filter(docente=profesor_jefe).first()
                    if jefatura_existente:
                        return JsonResponse({
                            'success': False,
                            'errors': {'__all__': [f'El profesor {profesor_jefe.usuario.nombre} {profesor_jefe.usuario.apellido_paterno} ya es jefe del curso {jefatura_existente.curso}']}
                        })

                    # Crear el curso
                    curso = Curso.objects.create(nivel=nivel, letra=letra)

                    # Asignar el profesor jefe
                    ProfesorJefe.objects.create(docente=profesor_jefe, curso=curso)

                    return JsonResponse({
                        'success': True,
                        'message': f'Curso {nivel}°{letra} creado exitosamente'
                    })

                except Docente.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'errors': {'__all__': ['El profesor seleccionado no existe']}
                    })
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'errors': {'__all__': [f'Error al crear el curso: {str(e)}']}
                    })
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
            print(f"Usuario autenticado: {request.user.is_authenticated}")
            print(f"Es admin: {request.user.is_admin}")
            print(f"User ID: {user_id}")
            print(f"Request user: {request.user}")
            print(f"Request user type: {type(request.user)}")
            print(f"Request user attributes: {dir(request.user)}")
            
            # Verificar si el usuario está autenticado
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'error': 'Usuario no autenticado'})
            
            # Verificar si el usuario es administrador
            if not hasattr(request.user, 'is_admin') or not request.user.is_admin:
                return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'})
            
            usuario = get_object_or_404(Usuario, id=user_id)
            print(f"Usuario encontrado: {usuario}")
            
            # No permitir desactivar administradores máximos
            if hasattr(usuario, 'administrativo') and usuario.administrativo.rol == 'ADMINISTRADOR_MAXIMO':
                return JsonResponse({'success': False, 'error': 'No se puede desactivar un administrador máximo'})
            
            # Invertir el estado actual
            usuario.activador = not usuario.activador
            usuario.save()
            print(f"Nuevo estado: {usuario.activador}")
            
            return JsonResponse({
                'success': True,
                'is_active': usuario.activador
            })
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
