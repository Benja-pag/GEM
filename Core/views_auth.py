from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from .models import Usuario, AuthUser
from django.contrib.auth.hashers import make_password

class LoginView(View):
    template_name = 'auth/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        rut = request.POST.get('rut')
        div = request.POST.get('div')
        password = request.POST.get('password')

        if not all([rut, div, password]):
            messages.error(request, 'Por favor complete todos los campos')
            return render(request, self.template_name)

        user = authenticate(request, rut=rut, div=div, password=password)
        if user is not None:
            login(request, user)
            # Redirigir según el tipo de usuario
            if hasattr(user, 'administrativo'):
                return redirect('admin_panel')
            elif hasattr(user, 'docente'):
                return redirect('profesor_panel')
            elif hasattr(user, 'estudiante'):
                return redirect('estudiante_panel')
            return redirect('home')
        else:
            messages.error(request, 'RUT o contraseña incorrectos')
            return render(request, self.template_name)

class LogoutView(View):
    def get(self, request):
        logout(request)
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