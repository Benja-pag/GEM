from django.db import transaction
from .models import Clase, Sala

class ClassService:
    @staticmethod
    def create_class(nombre, curso, profesor_jefe):
        """Crea una nueva clase"""
        try:
            with transaction.atomic():
                clase = Clase.objects.create(
                    nombre=nombre,
                    curso=curso,
                    profesor_jefe=profesor_jefe
                )
                return clase
        except Exception as e:
            raise Exception(f"Error al crear clase: {str(e)}")

    @staticmethod
    def add_student_to_class(clase_id, student_id):
        """Agrega un estudiante a una clase"""
        try:
            with transaction.atomic():
                clase = Clase.objects.get(id=clase_id)
                clase.alumnos.add(student_id)
                return clase
        except Clase.DoesNotExist:
            raise Exception("Clase no encontrada")
        except Exception as e:
            raise Exception(f"Error al agregar estudiante: {str(e)}")

    @staticmethod
    def remove_student_from_class(clase_id, student_id):
        """Elimina un estudiante de una clase"""
        try:
            with transaction.atomic():
                clase = Clase.objects.get(id=clase_id)
                clase.alumnos.remove(student_id)
                return clase
        except Clase.DoesNotExist:
            raise Exception("Clase no encontrada")
        except Exception as e:
            raise Exception(f"Error al eliminar estudiante: {str(e)}")

    @staticmethod
    def create_room(nombre, capacidad, ubicacion):
        """Crea una nueva sala"""
        try:
            with transaction.atomic():
                sala = Sala.objects.create(
                    nombre=nombre,
                    capacidad=capacidad,
                    ubicacion=ubicacion
                )
                return sala
        except Exception as e:
            raise Exception(f"Error al crear sala: {str(e)}")

    @staticmethod
    def get_teacher_classes(teacher_id):
        """Obtiene todas las clases de un profesor"""
        try:
            return Clase.objects.filter(profesor_jefe_id=teacher_id)
        except Exception as e:
            raise Exception(f"Error al obtener clases: {str(e)}")

    @staticmethod
    def get_student_classes(student_id):
        """Obtiene todas las clases de un estudiante"""
        try:
            return Clase.objects.filter(alumnos__id=student_id)
        except Exception as e:
            raise Exception(f"Error al obtener clases: {str(e)}") 