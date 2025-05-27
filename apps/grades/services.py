from django.db import transaction
from django.db.models import Avg
from .models import Calificacion, Promedio

class GradeService:
    @staticmethod
    def create_grade(alumno, asignatura, nota, fecha, tipo, comentario=None):
        """Crea una nueva calificación"""
        try:
            with transaction.atomic():
                calificacion = Calificacion.objects.create(
                    alumno=alumno,
                    asignatura=asignatura,
                    nota=nota,
                    fecha=fecha,
                    tipo=tipo,
                    comentario=comentario
                )
                return calificacion
        except Exception as e:
            raise Exception(f"Error al crear calificación: {str(e)}")

    @staticmethod
    def calculate_average(alumno, asignatura, periodo):
        """Calcula el promedio de un alumno en una asignatura para un período"""
        try:
            with transaction.atomic():
                # Obtener todas las calificaciones del alumno en la asignatura
                calificaciones = Calificacion.objects.filter(
                    alumno=alumno,
                    asignatura=asignatura
                )
                
                # Calcular el promedio
                promedio = calificaciones.aggregate(Avg('nota'))['nota__avg']
                
                if promedio is not None:
                    # Crear o actualizar el registro de promedio
                    promedio_obj, created = Promedio.objects.update_or_create(
                        alumno=alumno,
                        asignatura=asignatura,
                        periodo=periodo,
                        defaults={'promedio': promedio}
                    )
                    return promedio_obj
                else:
                    raise Exception("No hay calificaciones para calcular el promedio")
        except Exception as e:
            raise Exception(f"Error al calcular promedio: {str(e)}")

    @staticmethod
    def get_student_grades(student_id, subject_id=None):
        """Obtiene todas las calificaciones de un estudiante"""
        try:
            query = Calificacion.objects.filter(alumno_id=student_id)
            if subject_id:
                query = query.filter(asignatura_id=subject_id)
            return query
        except Exception as e:
            raise Exception(f"Error al obtener calificaciones: {str(e)}")

    @staticmethod
    def get_student_averages(student_id, subject_id=None):
        """Obtiene todos los promedios de un estudiante"""
        try:
            query = Promedio.objects.filter(alumno_id=student_id)
            if subject_id:
                query = query.filter(asignatura_id=subject_id)
            return query
        except Exception as e:
            raise Exception(f"Error al obtener promedios: {str(e)}")

    @staticmethod
    def get_subject_grades(subject_id):
        """Obtiene todas las calificaciones de una asignatura"""
        try:
            return Calificacion.objects.filter(asignatura_id=subject_id)
        except Exception as e:
            raise Exception(f"Error al obtener calificaciones: {str(e)}") 