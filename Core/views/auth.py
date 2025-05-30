from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from Core.models import Usuario
from django.contrib.auth.hashers import make_password, check_password
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from Core.servicios.helpers.validadores import validar_data_crear_usuario
from Core.servicios.repos.usuarios import crear_usuario, obtener_usuario_por_correo
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages




class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        print(correo)
        
        if not correo or not password:
            messages.error(request, 'Por favor ingrese correo y contraseña')
            return render(request, self.template_name)

        try:
            usuario = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            messages.error(request, 'El correo no está registrado')
            return render(request, self.template_name)

        auth_user = usuario.auth_user
        status_ok, template = self.check_user_status(usuario, auth_user, messages)
        if not status_ok:
            return render(request, template)

        if check_password(password, auth_user.password):
            login(request, auth_user)
            return self.redirect_by_role(usuario, auth_user)
        else:
            messages.error(request, 'Contraseña incorrecta')
            return render(request, self.template_name)
        
    def check_user_status(self, usuario, auth_user, messages):
        if not auth_user.is_active:
            messages.error(
                None, 'Usuario desactivado. Por favor comuníquese con un administrador.'
            )
            return False, 'login.html'
        if not usuario.activador:
            messages.error(
                None, 'Su cuenta está inactiva. Por favor comuníquese con un administrador.'
            )
            return False, 'login.html'
        return True, None

    def redirect_by_role( self, usuario, auth_user):
        if auth_user.is_admin:
            return redirect('admin_panel')
        elif hasattr(usuario, 'docente'):
            return redirect('profesor_panel')
        elif hasattr(usuario, 'estudiante'):
            return redirect('estudiante_panel')
        else:
            messages.error(None, 'Tipo de usuario no válido')
            return redirect('login')

@method_decorator(login_required, name='dispatch') 
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
            success = validar_data_crear_usuario(request.POST) 
            if not success:
                return render(request, self.template_name)

            if request.POST['tipo_usuario'] == 'ADMINISTRATIVO':
                messages.error(request, 'No se puede crear un administrador desde el registro.')
                return render(request, self.template_name)
            # Crear el usuario
            crear_usuario(request.POST, request.POST['tipo_usuario'])
            # Redirigir al login después de registrar
            messages.success(request, 'Usuario registrado exitosamente')
            return redirect('login')

        except Exception as e:
            messages.error(request, f'Error al registrar usuario: {str(e)}')
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
