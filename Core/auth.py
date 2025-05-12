from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import AuthUser, Usuario

class EmailBackend(BaseBackend):
    def authenticate(self, request, correo=None, password=None):
        try:
            # Buscar el usuario por correo
            usuario = Usuario.objects.get(correo=correo)
            auth_user = usuario.auth_user
            
            # Verificar la contraseña
            if check_password(password, auth_user.password):
                # Actualizar last_login
                auth_user.save()
                # Retornar el usuario de autenticación
                return auth_user
        except Usuario.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return AuthUser.objects.get(id=user_id)
        except AuthUser.DoesNotExist:
            return None 