from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, Nota, AuthUser, Asignatura
from django.db.models import Count, Avg
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.db import transaction

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                usuario = Usuario.objects.get(auth_user=self.request.user)
                context['usuario'] = usuario
            except Usuario.DoesNotExist:
                messages.error(self.request, 'Error: Usuario no encontrado')
        return context

@method_decorator(login_required, name='dispatch')
class AdminPanelView(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            return redirect('login')
        try:
            # Obtener estadísticas
            total_estudiantes = Usuario.objects.filter(estudiante__isnull=False).count()
            total_profesores = Usuario.objects.filter(docente__isnull=False).count()
            total_clases = Clase.objects.count()
            total_cursos = Asignatura.objects.count()  # Total de asignaturas
            # Obtener usuarios
            usuarios = Usuario.objects.all().order_by('-fecha_creacion')
            # Obtener todas las clases sin límite
            clases = Clase.objects.all().order_by('nombre')
            # Obtener todas las asignaturas
            asignaturas = Asignatura.objects.all().order_by('codigo')
            context = {
                'total_estudiantes': total_estudiantes,
                'total_profesores': total_profesores,
                'total_clases': total_clases,
                'total_cursos': total_cursos,
                'usuarios': usuarios,
                'clases': clases,
                'asignaturas': asignaturas,
                'now': timezone.now(),
            }
            return render(request, 'admin_panel.html', context)
        except Exception as e:
            messages.error(request, f'Error al cargar el panel de administrador: {str(e)}')
            return redirect('home')

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
            tipo_usuario = request.POST.get('tipo_usuario')
            rol_administrativo = request.POST.get('rol_administrativo')

            # Validar campos requeridos
            if not all([nombre, apellido_paterno, apellido_materno, rut, div, correo, password, confirm_password, tipo_usuario]):
                messages.error(request, 'Por favor complete todos los campos requeridos')
                return redirect('admin_panel')

            # Validar contraseñas
            if password != confirm_password:
                messages.error(request, 'Las contraseñas no coinciden')
                return redirect('admin_panel')

            # Verificar si el RUT ya existe
            if Usuario.objects.filter(rut=rut).exists():
                messages.error(request, 'El RUT ya está registrado')
                return redirect('admin_panel')

            # Verificar si el correo ya existe
            if Usuario.objects.filter(correo=correo).exists():
                messages.error(request, 'El correo ya está registrado')
                return redirect('admin_panel')

            # Crear usuario de autenticación
            auth_user = AuthUser.objects.create(
                rut=rut,
                div=div,
                password=make_password(password),
                is_admin=(tipo_usuario in ['ADMINISTRADOR', 'ADMINISTRADOR_MAXIMO'])
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

            # Crear el tipo de usuario correspondiente
            if tipo_usuario == 'ESTUDIANTE':
                contacto_emergencia = request.POST.get('contacto_emergencia')
                if not contacto_emergencia:
                    messages.error(request, 'El contacto de emergencia es requerido para estudiantes')
                    usuario.delete()
                    auth_user.delete()
                    return redirect('admin_panel')
                Estudiante.objects.create(
                    usuario=usuario,
                    contacto_emergencia=contacto_emergencia
                )
            elif tipo_usuario == 'PROFESOR':
                Docente.objects.create(usuario=usuario)
            elif tipo_usuario in ['ADMINISTRADOR', 'ADMINISTRADOR_MAXIMO']:
                Administrativo.objects.create(
                    usuario=usuario,
                    rol=rol_administrativo or tipo_usuario
                )

            messages.success(request, f'Usuario {tipo_usuario.lower()} creado exitosamente')
            return redirect('admin_panel')
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
            return redirect('admin_panel')

@method_decorator(login_required, name='dispatch')
class UserManagementView(View):
    def get(self, request):
        if not request.user.is_admin:
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        
        users = Usuario.objects.all().order_by('-fecha_creacion')
        context = {
            'users': users,
            'total_estudiantes': Usuario.objects.filter(estudiante__isnull=False).count(),
            'total_profesores': Usuario.objects.filter(docente__isnull=False).count(),
            'total_clases': Clase.objects.count(),
            'clases': Clase.objects.all().order_by('nombre')[:10],
            'now': timezone.now(),
        }
        return render(request, 'admin_panel.html', context)

@method_decorator(login_required, name='dispatch')
class UserCreateView(View):
    def get(self, request):
        if not request.user.administrativo:
            messages.error(request, 'No tienes permiso para acceder a esta página.')
            return redirect('home')
        return render(request, 'user_create.html')

    def post(self, request):
        if not request.user.administrativo:
            return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción.'})

        try:
            with transaction.atomic():
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
                tipo_usuario = request.POST.get('tipo_usuario')

                # Validar campos requeridos
                if not all([nombre, apellido_paterno, rut, div, correo, password, confirm_password, tipo_usuario]):
                    return JsonResponse({'success': False, 'error': 'Todos los campos marcados con * son obligatorios.'})

                # Validar contraseñas
                if password != confirm_password:
                    return JsonResponse({'success': False, 'error': 'Las contraseñas no coinciden.'})

                # Validar RUT único
                if AuthUser.objects.filter(rut=rut, div=div).exists():
                    return JsonResponse({'success': False, 'error': 'El RUT ya está registrado.'})

                # Validar correo único
                if AuthUser.objects.filter(correo=correo).exists():
                    return JsonResponse({'success': False, 'error': 'El correo electrónico ya está registrado.'})

                # Crear usuario de autenticación
                auth_user = AuthUser.objects.create(
                    rut=rut,
                    div=div,
                    correo=correo,
                    telefono=telefono,
                    direccion=direccion,
                    fecha_nacimiento=fecha_nacimiento,
                    fecha_creacion=timezone.now(),
                    fecha_actualizacion=timezone.now()
                )
                auth_user.set_password(password)
                auth_user.save()

                # Crear usuario
                usuario = Usuario.objects.create(
                    auth_user=auth_user,
                    nombre=nombre,
                    apellido_paterno=apellido_paterno,
                    apellido_materno=apellido_materno,
                    fecha_creacion=timezone.now(),
                    fecha_actualizacion=timezone.now()
                )

                # Crear tipo de usuario específico
                if tipo_usuario == 'DOCENTE':
                    Docente.objects.create(usuario=usuario)
                elif tipo_usuario == 'ESTUDIANTE':
                    Estudiante.objects.create(usuario=usuario)
                elif tipo_usuario == 'ADMINISTRATIVO':
                    Administrativo.objects.create(usuario=usuario)

                return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class UserDetailView(View):
    def get(self, request, user_id):
        try:
            user = get_object_or_404(Usuario, id=user_id)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': user.id,
                        'nombre': user.nombre,
                        'apellido_paterno': user.apellido_paterno,
                        'apellido_materno': user.apellido_materno,
                        'rut': user.rut,
                        'div': user.div,
                        'correo': user.correo,
                        'telefono': user.telefono,
                        'direccion': user.direccion,
                        'fecha_nacimiento': user.fecha_nacimiento
                    }
                })
            return redirect('admin_panel')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, str(e))
            return redirect('admin_panel')

@method_decorator(csrf_exempt, name='dispatch')
class UserUpdateView(View):
    def get(self, request, user_id):
        try:
            user = get_object_or_404(Usuario, id=user_id)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': user.id,
                        'nombre': user.nombre,
                        'apellido_paterno': user.apellido_paterno,
                        'apellido_materno': user.apellido_materno,
                        'rut': user.rut,
                        'div': user.div,
                        'correo': user.correo,
                        'telefono': user.telefono,
                        'direccion': user.direccion,
                        'fecha_nacimiento': user.fecha_nacimiento
                    }
                })
            return redirect('admin_panel')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, str(e))
            return redirect('admin_panel')

    def post(self, request, user_id):
        try:
            user = get_object_or_404(Usuario, id=user_id)
            user.nombre = request.POST.get('nombre')
            user.apellido_paterno = request.POST.get('apellido_paterno')
            user.apellido_materno = request.POST.get('apellido_materno')
            user.rut = request.POST.get('rut')
            user.div = request.POST.get('div')
            user.correo = request.POST.get('correo')
            user.telefono = request.POST.get('telefono')
            user.direccion = request.POST.get('direccion')
            user.fecha_nacimiento = request.POST.get('fecha_nacimiento')
            user.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            messages.success(request, 'Usuario actualizado exitosamente')
            return redirect('admin_panel')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, str(e))
            return redirect('admin_panel')

@method_decorator(csrf_exempt, name='dispatch')
class UserDeleteView(View):
    def post(self, request, user_id):
        try:
            usuario = get_object_or_404(Usuario, id=user_id)
            
            # Verificar si es un administrador máximo
            if hasattr(usuario, 'administrativo') and usuario.administrativo.rol == 'ADMINISTRADOR':
                # Contar cuántos administradores máximos hay
                total_admins = Administrativo.objects.filter(rol='ADMINISTRADOR').count()
                
                # Si es el único administrador máximo, no permitir eliminarlo
                if total_admins <= 1:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False, 
                            'error': 'No se puede eliminar el último administrador máximo. Debe haber al menos un administrador máximo en el sistema.'
                        })
                    messages.error(request, 'No se puede eliminar el último administrador máximo. Debe haber al menos un administrador máximo en el sistema.')
                    return redirect('admin_panel')
            
            # Si no es el último administrador máximo o no es administrador, proceder con la eliminación
            usuario.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            messages.success(request, 'Usuario eliminado exitosamente')
            return redirect('admin_panel')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, str(e))
            return redirect('admin_panel')

@method_decorator(login_required, name='dispatch')
class ProfesorPanelView(View):
    def get(self, request):
        if not hasattr(request.user.usuario, 'docente'):
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        
        docente = request.user.usuario.docente
        # Obtener clases donde el docente es profesor jefe
        clases_profesor_jefe = Clase.objects.filter(profesor_jefe=docente)
        # Obtener clases donde el docente imparte asignaturas
        clases_asignaturas = Clase.objects.filter(asignatura__docente=docente)
        # Combinar ambas querysets
        clases = (clases_profesor_jefe | clases_asignaturas).distinct()
        # Obtener las notas de las asignaturas que imparte el docente
        notas = Nota.objects.filter(asignatura__docente=docente)
        
        context = {
            'clases': clases,
            'notas': notas
        }
        return render(request, 'teacher_panel.html', context)

@method_decorator(login_required, name='dispatch')
class EstudiantePanelView(View):
    def get(self, request):
        if not hasattr(request.user.usuario, 'estudiante'):
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        estudiante = Estudiante.objects.first()  # Temporalmente mostramos el primer estudiante
        notas = Nota.objects.filter(estudiante=estudiante)
        asistencias = Asistencia.objects.filter(estudiante=estudiante)
        
        context = {
            'notas': notas,
            'asistencias': asistencias
        }
        return render(request, 'students_panel.html', context)

@method_decorator(login_required, name='dispatch')
class AttendanceView(TemplateView):
    template_name = 'attendance.html'
    
    def get(self, request, *args, **kwargs):
        if not (request.user.is_admin or hasattr(request.user.usuario, 'docente')):
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        return super().get(request, *args, **kwargs)

def login_view(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        
        if not correo or not password:
            messages.error(request, 'Por favor ingrese correo y contraseña')
            return render(request, 'login.html')
        
        try:
            # Buscar el usuario por correo en el modelo Usuario
            usuario = Usuario.objects.get(correo=correo)
            # Obtener el AuthUser asociado
            auth_user = usuario.auth_user
            
            # Verificar si el usuario está activo
            if not auth_user.is_active:
                messages.error(request, 'Usuario desactivado. Por favor comuníquese con un administrador.')
                return render(request, 'login.html')
            
            # Verificar la contraseña usando check_password
            if check_password(password, auth_user.password):
                login(request, auth_user)
                # Redirigir según el rol del usuario
                if auth_user.is_admin:
                    return redirect('admin_panel')
                elif hasattr(usuario, 'docente'):
                    return redirect('profesor_panel')
                elif hasattr(usuario, 'estudiante'):
                    return redirect('estudiante_panel')
                else:
                    messages.error(request, 'Tipo de usuario no válido')
                    return redirect('login')
            else:
                messages.error(request, 'Contraseña incorrecta')
        except Usuario.DoesNotExist:
            messages.error(request, 'El correo no está registrado')
    
    return render(request, 'login.html')

class LogoutView(View):
    def post(self, request):
        # Limpiar la sesión
        request.session.flush()
        # Cerrar la sesión de Django
        logout(request)
        # Redirigir al login con un mensaje
        messages.success(request, 'Has cerrado sesión exitosamente')
        return redirect('login')

class RegisterView(View):
    template_name = 'auth/register.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
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
            tipo_usuario = request.POST.get('tipo_usuario', 'ESTUDIANTE')  # Por defecto es estudiante

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

            # Crear usuario de autenticación
            auth_user = AuthUser.objects.create(
                rut=rut,
                div=div,
                password=make_password(password)
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

            # Crear el tipo de usuario correspondiente
            if tipo_usuario == 'DOCENTE':
                Docente.objects.create(usuario=usuario)
            else:  # Por defecto es estudiante
                Estudiante.objects.create(usuario=usuario)

            messages.success(request, 'Usuario registrado exitosamente')
            return redirect('login')

        except Exception as e:
            messages.error(request, f'Error al registrar usuario: {str(e)}')
            return render(request, self.template_name)

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

class ChangePasswordView(View):
    template_name = 'auth/change_password.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        try:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not all([current_password, new_password, confirm_password]):
                messages.error(request, 'Por favor complete todos los campos')
                return render(request, self.template_name)

            if new_password != confirm_password:
                messages.error(request, 'Las contraseñas no coinciden')
                return render(request, self.template_name)

            # Verificar contraseña actual
            auth_user = request.user.auth_user
            if not auth_user.check_password(current_password):
                messages.error(request, 'Contraseña actual incorrecta')
                return render(request, self.template_name)

            # Actualizar contraseña
            auth_user.password = make_password(new_password)
            auth_user.save()

            messages.success(request, 'Contraseña actualizada exitosamente')
            return redirect('home')

        except Exception as e:
            messages.error(request, f'Error al cambiar contraseña: {str(e)}')
            return render(request, self.template_name)

@method_decorator(csrf_exempt, name='dispatch')
class UserToggleStatusView(View):
    def post(self, request, user_id):
        try:
            if not request.user.is_admin:
                return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'})
            
            usuario = get_object_or_404(Usuario, id=user_id)
            # Invertir el estado actual
            usuario.auth_user.is_active = not usuario.auth_user.is_active
            usuario.auth_user.save()
            
            return JsonResponse({
                'success': True,
                'is_active': usuario.auth_user.is_active
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class UserDataView(View):
    def get(self, request, user_id):
        try:
            # Separar el RUT y el dígito verificador
            rut_parts = user_id.split('-')
            if len(rut_parts) != 2:
                return JsonResponse({'success': False, 'error': 'Formato de RUT inválido'})
            
            rut = rut_parts[0]
            div = rut_parts[1]
            
            usuario = get_object_or_404(Usuario, rut=rut, div=div)
            data = {
                'success': True,
                'data': {
                    'nombre': usuario.nombre,
                    'apellido_paterno': usuario.apellido_paterno,
                    'apellido_materno': usuario.apellido_materno,
                    'rut': usuario.rut,
                    'div': usuario.div,
                    'correo': usuario.correo,
                    'telefono': usuario.telefono,
                    'direccion': usuario.direccion,
                    'fecha_nacimiento': usuario.fecha_nacimiento.strftime('%Y-%m-%d') if usuario.fecha_nacimiento else None,
                    'tipo_usuario': 'estudiante' if hasattr(usuario, 'estudiante') else 'docente' if hasattr(usuario, 'docente') else 'administrativo',
                }
            }
            
            # Agregar datos específicos según el tipo de usuario
            if hasattr(usuario, 'estudiante'):
                data['data']['contacto_emergencia'] = usuario.estudiante.contacto_emergencia
            elif hasattr(usuario, 'administrativo'):
                data['data']['rol_administrativo'] = usuario.administrativo.rol
            
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def post(self, request, user_id):
        try:
            # Verificar que el usuario que hace la petición es docente o administrador
            if not (hasattr(request.user.usuario, 'docente') or hasattr(request.user.usuario, 'administrativo')):
                return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'})

            # Separar el RUT y el dígito verificador
            rut_parts = user_id.split('-')
            if len(rut_parts) != 2:
                return JsonResponse({'success': False, 'error': 'Formato de RUT inválido'})
            
            rut = rut_parts[0]
            div = rut_parts[1]
            
            usuario = get_object_or_404(Usuario, rut=rut, div=div)
            
            # Verificar si el usuario es administrador máximo
            if hasattr(usuario, 'administrativo') and usuario.administrativo.rol == 'ADMINISTRADOR_MAXIMO':
                return JsonResponse({'success': False, 'error': 'No se puede modificar un administrador máximo'})
            
            # Actualizar datos básicos
            usuario.nombre = request.POST.get('nombre')
            usuario.apellido_paterno = request.POST.get('apellido_paterno')
            usuario.apellido_materno = request.POST.get('apellido_materno')
            usuario.rut = request.POST.get('rut')
            usuario.div = request.POST.get('div')
            usuario.correo = request.POST.get('correo')
            usuario.telefono = request.POST.get('telefono')
            usuario.direccion = request.POST.get('direccion')
            usuario.fecha_nacimiento = request.POST.get('fecha_nacimiento')
            usuario.save()
            
            # Actualizar datos de AuthUser
            auth_user = usuario.auth_user
            auth_user.rut = request.POST.get('rut')
            auth_user.div = request.POST.get('div')
            auth_user.correo = request.POST.get('correo')
            auth_user.telefono = request.POST.get('telefono')
            auth_user.direccion = request.POST.get('direccion')
            auth_user.fecha_nacimiento = request.POST.get('fecha_nacimiento')
            auth_user.save()
            
            # Manejar cambio de tipo de usuario
            nuevo_tipo = request.POST.get('tipo_usuario')
            tipo_actual = 'estudiante' if hasattr(usuario, 'estudiante') else 'docente' if hasattr(usuario, 'docente') else 'administrativo'
            
            # Solo permitir cambio de tipo si el usuario que hace la petición es administrador
            if nuevo_tipo != tipo_actual and hasattr(request.user.usuario, 'administrativo'):
                # Eliminar el tipo actual
                if hasattr(usuario, 'estudiante'):
                    usuario.estudiante.delete()
                elif hasattr(usuario, 'docente'):
                    usuario.docente.delete()
                elif hasattr(usuario, 'administrativo'):
                    usuario.administrativo.delete()
                
                # Crear el nuevo tipo
                if nuevo_tipo == 'estudiante':
                    Estudiante.objects.create(
                        usuario=usuario,
                        contacto_emergencia=request.POST.get('contacto_emergencia')
                    )
                elif nuevo_tipo == 'docente':
                    Docente.objects.create(usuario=usuario)
                elif nuevo_tipo == 'administrativo':
                    Administrativo.objects.create(
                        usuario=usuario,
                        rol='ADMINISTRADOR'  # Siempre se crea como administrador normal
                    )
            
            # Actualizar datos específicos según el tipo de usuario
            if nuevo_tipo == 'estudiante' and hasattr(usuario, 'estudiante'):
                usuario.estudiante.contacto_emergencia = request.POST.get('contacto_emergencia')
                usuario.estudiante.save()
            elif nuevo_tipo == 'administrativo' and hasattr(usuario, 'administrativo'):
                usuario.administrativo.rol = 'ADMINISTRADOR'  # Siempre se mantiene como administrador normal
                usuario.administrativo.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})