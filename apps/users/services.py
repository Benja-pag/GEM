from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Estudiante, Docente

Usuario = get_user_model()

class UserService:
    @staticmethod
    def create_user(email, password, nombre, apellido, **kwargs):
        """Crea un nuevo usuario"""
        try:
            with transaction.atomic():
                user = Usuario.objects.create_user(
                    email=email,
                    password=password,
                    nombre=nombre,
                    apellido=apellido,
                    **kwargs
                )
                return user
        except Exception as e:
            raise Exception(f"Error al crear usuario: {str(e)}")

    @staticmethod
    def create_student(user, rut, fecha_nacimiento, direccion, telefono):
        """Crea un nuevo estudiante"""
        try:
            with transaction.atomic():
                estudiante = Estudiante.objects.create(
                    usuario=user,
                    rut=rut,
                    fecha_nacimiento=fecha_nacimiento,
                    direccion=direccion,
                    telefono=telefono
                )
                return estudiante
        except Exception as e:
            raise Exception(f"Error al crear estudiante: {str(e)}")

    @staticmethod
    def create_teacher(user, rut, especialidad, telefono):
        """Crea un nuevo docente"""
        try:
            with transaction.atomic():
                docente = Docente.objects.create(
                    usuario=user,
                    rut=rut,
                    especialidad=especialidad,
                    telefono=telefono
                )
                return docente
        except Exception as e:
            raise Exception(f"Error al crear docente: {str(e)}")

    @staticmethod
    def update_user(user_id, **kwargs):
        """Actualiza un usuario existente"""
        try:
            user = Usuario.objects.get(id=user_id)
            for key, value in kwargs.items():
                setattr(user, key, value)
            user.save()
            return user
        except Usuario.DoesNotExist:
            raise Exception("Usuario no encontrado")

    @staticmethod
    def deactivate_user(user_id):
        """Desactiva un usuario"""
        try:
            user = Usuario.objects.get(id=user_id)
            user.is_active = False
            user.save()
            return user
        except Usuario.DoesNotExist:
            raise Exception("Usuario no encontrado") 