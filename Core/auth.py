from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import AuthUser, Usuario

class RUTBackend(BaseBackend):
    def authenticate(self, request, rut=None, div=None, password=None):
        try:
            # Buscar el usuario por RUT y dígito verificador
            auth_user = AuthUser.objects.get(rut=rut, div=div)
            
            # Verificar la contraseña
            if check_password(password, auth_user.password):
                # Actualizar last_login
                auth_user.save()
                # Retornar el usuario de autenticación
                return auth_user
        except AuthUser.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return AuthUser.objects.get(id=user_id)
        except AuthUser.DoesNotExist:
            return None 