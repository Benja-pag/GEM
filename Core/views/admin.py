from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from Core.models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura, AsignaturaImpartida
from django.db.models import Count, Avg
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from Core.servicios.repos import usuarios
from Core.servicios.helpers import validadores, serializadores

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
            
            # Obtener profesores para el formulario de creación de curso
            profesores = Docente.objects.all()
            
            # Obtener todos los estudiantes
            estudiantes_sin_curso = Estudiante.objects.all().select_related('usuario', 'clase')
            
            # Obtener todos los usuarios ordenados por fecha de creación
            usuarios = Usuario.objects.all().order_by('-fecha_creacion')
            
            # Obtener todas las asignaturas
            asignaturas = Asignatura.objects.all()
            
            context = {
                'total_estudiantes': total_estudiantes,
                'total_profesores': total_profesores,
                'total_asignaturas_impartidas': total_asignaturas_impartidas,
                'total_administradores': total_administradores,
                'profesores': profesores,
                'estudiantes_sin_curso': estudiantes_sin_curso,
                'usuarios': usuarios,
                'asignaturas': asignaturas
            }
            return render(request, 'admin_panel.html', context)
        except Exception as e:
            messages.error(request, f'Error al cargar el panel de administrador: {str(e)}')
            return redirect('home')


    ### Esto no debería estar aquí, pero lo dejaremos por ahora
    ### la idea es que cada acción tenga su propia vista y el front se encargue de llamarla
    def post(self, request):
        if not request.user.is_admin:
            messages.error(request, 'No tienes permiso para realizar esta acción')
            return redirect('home')
        
        action = request.POST.get('action')
        
        try:
            if action == 'crear_estudiante':
                return self.crear_estudiante(request)
            elif action == 'crear_profesor':
                return self.crear_profesor(request)
            elif action == 'crear_administrador':
                return self.crear_administrador(request)
            elif action == 'crear_curso':
                return self.crear_curso(request)
            elif action == 'crear_asignatura':
                return self.crear_asignatura(request)
            else:
                messages.error(request, 'Acción no válida')
                return redirect('admin_panel')
        except Exception as e:
            messages.error(request, f'Error al procesar la solicitud: {str(e)}')
            return redirect('admin_panel')
             
    def crear_estudiante(self, request):
        try:
            usuarios.crear_usuario(request.POST, 'ESTUDIANTE')
            messages.success(request, 'Estudiante creado exitosamente')
            return redirect('admin_panel')
        except Exception as e:
            messages.error(request, f'Error al crear estudiante: {str(e)}')
            return redirect('admin_panel')

    def crear_profesor(self, request):
        try:
            usuarios.crear_usuario(request.POST, 'DOCENTE')
            messages.success(request, 'Profesor creado exitosamente')
            return redirect('admin_panel')
        except Exception as e:
            messages.error(request, f'Error al crear profesor: {str(e)}')
            return redirect('admin_panel')

    def crear_administrador(self, request):
        try:     
            usuarios.crear_usuario(request.POST, 'ADMINISTRATIVO')
            messages.success(request, 'Administrador creado exitosamente')
            return redirect('admin_panel')
        except Exception as e:
            messages.error(request, f'Error al crear administrador: {str(e)}')
            return redirect('admin_panel')

    def crear_curso(self, request):
        try:
            with transaction.atomic():
                # Crear curso
                Clase.objects.create(
                    nombre=request.POST.get('nombre'),
                    profesor_jefe_id=request.POST.get('profesor_jefe'),
                    sala=request.POST.get('sala'),
                    capacidad=request.POST.get('capacidad')
                )

                messages.success(request, 'Curso creado exitosamente')
                return redirect('admin_panel')
        except Exception as e:
            messages.error(request, f'Error al crear curso: {str(e)}')
            return redirect('admin_panel')

    def crear_asignatura(self, request):
        try:
            with transaction.atomic():
                # Crear asignatura
                Asignatura.objects.create(
                    codigo=request.POST.get('codigo'),
                    nombre=request.POST.get('nombre'),
                    clase_id=request.POST.get('clase'),
                    docente_id=request.POST.get('docente'),
                    dia=request.POST.get('dia'),
                    horario=request.POST.get('horario')
                )

                messages.success(request, 'Asignatura creada exitosamente')
                return redirect('admin_panel')
        except Exception as e:
            messages.error(request, f'Error al crear asignatura: {str(e)}')
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
