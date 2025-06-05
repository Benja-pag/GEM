from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from Core.models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura, AsignaturaImpartida, Curso, ProfesorJefe
from django.db.models import Count, Avg
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from Core.servicios.repos import usuarios
from Core.servicios.helpers import validadores, serializadores
from ..forms import EstudianteForm, DocenteForm, AdministrativoForm, CursoForm, AsignaturaForm, ProfesorJefeForm
from Core.servicios.repos.usuarios import crear_usuario, actualizar_usuario

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
            
            # Obtener profesores para el formulario de creación de curso
            profesores = Docente.objects.all()
            
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
            
            # Inicializar formularios
            estudiante_form = EstudianteForm()
            docente_form = DocenteForm()
            administrativo_form = AdministrativoForm()
            curso_form = CursoForm()
            asignatura_form = AsignaturaForm()
            profesor_jefe_form = ProfesorJefeForm()
            
            context = {
                'total_estudiantes': total_estudiantes,
                'total_profesores': total_profesores,
                'total_asignaturas_impartidas': total_asignaturas_impartidas,
                'total_administradores': total_administradores,
                'total_clases': total_clases,
                'total_asignaturas': total_asignaturas,
                'profesores': profesores,
                'estudiantes_sin_curso': estudiantes_sin_curso,
                'usuarios': usuarios,
                'asignaturas': asignaturas,
                'cursos': cursos,
                'estudiante_form': estudiante_form,
                'docente_form': docente_form,
                'administrativo_form': administrativo_form,
                'curso_form': curso_form,
                'asignatura_form': asignatura_form,
                'profesor_jefe_form': profesor_jefe_form,
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
                form = EstudianteForm(request.POST)
                if form.is_valid():
                    data = form.cleaned_data
                    data['tipo_usuario'] = 'ESTUDIANTE'
                    crear_usuario(data, 'ESTUDIANTE')
                    messages.success(request, 'Estudiante creado exitosamente')
                    return redirect('admin_panel')
                else:
                    estudiante_form = form
            elif action == 'crear_docente':
                form = DocenteForm(request.POST)
                if form.is_valid():
                    data = form.cleaned_data
                    data['tipo_usuario'] = 'DOCENTE'
                    crear_usuario(data, 'DOCENTE')
                    messages.success(request, 'Docente creado exitosamente')
                    return redirect('admin_panel')
                else:
                    docente_form = form
            elif action == 'crear_administrador':
                form = AdministrativoForm(request.POST)
                if form.is_valid():
                    data = form.cleaned_data
                    data['tipo_usuario'] = 'ADMINISTRATIVO'
                    crear_usuario(data, 'ADMINISTRATIVO')
                    messages.success(request, 'Administrador creado exitosamente')
                    return redirect('admin_panel')
                else:
                    administrativo_form = form
            elif action == 'crear_curso':
                form = CursoForm(request.POST)
                if form.is_valid():
                    curso = form.save()
                    # Si se proporcionó un docente, crear la jefatura
                    docente_id = request.POST.get('docente')
                    if docente_id:
                        ProfesorJefe.objects.create(
                            curso=curso,
                            docente_id=docente_id
                        )
                    messages.success(request, 'Curso creado exitosamente')
                    return redirect('admin_panel')
                else:
                    curso_form = form
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
            nombre = request.POST.get('nombre')
            apellido_paterno = request.POST.get('apellido_paterno')
            apellido_materno = request.POST.get('apellido_materno')
            rut = request.POST.get('rut')
            div = request.POST.get('div')
            correo = request.POST.get('correo')
            telefono = request.POST.get('telefono')
            direccion = request.POST.get('direccion')
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            rol = request.POST.get('rol', 'ADMINISTRATIVO')

            # Validar campos requeridos
            if not all([nombre, apellido_paterno, apellido_materno, rut, div, correo, password, confirm_password]):
                messages.error(request, 'Por favor complete todos los campos requeridos')
                return render(request, self.template_name)

            # Validar contraseñas
            if password != confirm_password:
                messages.error(request, 'Las contraseñas no coinciden')
                return render(request, self.template_name)

            # Verificar si el RUT ya existe
            if Usuario.objects.filter(rut=rut).exists():
                messages.error(request, 'El RUT ya está registrado')
                return render(request, self.template_name)

            # Verificar si el correo ya existe
            if Usuario.objects.filter(correo=correo).exists():
                messages.error(request, 'El correo ya está registrado')
                return render(request, self.template_name)

            # Crear usuario de autenticación con permisos de administrador
            auth_user = AuthUser.objects.create(
                rut=rut,
                div=div,
                password=make_password(password),
                is_admin=True
            )

            # Crear usuario
            usuario = Usuario.objects.create(
                nombre=nombre,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                rut=rut,
                div=div,
                correo=correo,
                telefono=telefono,
                direccion=direccion,
                fecha_nacimiento=fecha_nacimiento,
                auth_user=auth_user
            )

            # Crear administrativo
            Administrativo.objects.create(
                usuario=usuario,
                rol=rol
            )

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
