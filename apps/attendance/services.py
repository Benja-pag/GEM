from django.db import transaction
from .models import Asistencia, RegistroAsistencia

class AttendanceService:
    @staticmethod
    def create_attendance(alumno, asignatura, fecha, estado, justificacion=None):
        """Crea un nuevo registro de asistencia"""
        try:
            with transaction.atomic():
                asistencia = Asistencia.objects.create(
                    alumno=alumno,
                    asignatura=asignatura,
                    fecha=fecha,
                    estado=estado,
                    justificacion=justificacion
                )
                return asistencia
        except Exception as e:
            raise Exception(f"Error al crear asistencia: {str(e)}")

    @staticmethod
    def create_attendance_record(asignatura, fecha, profesor, observaciones=None):
        """Crea un nuevo registro de asistencia para una clase"""
        try:
            with transaction.atomic():
                registro = RegistroAsistencia.objects.create(
                    asignatura=asignatura,
                    fecha=fecha,
                    profesor=profesor,
                    observaciones=observaciones
                )
                return registro
        except Exception as e:
            raise Exception(f"Error al crear registro de asistencia: {str(e)}")

    @staticmethod
    def get_student_attendance(student_id, subject_id=None, start_date=None, end_date=None):
        """Obtiene los registros de asistencia de un estudiante"""
        try:
            query = Asistencia.objects.filter(alumno_id=student_id)
            if subject_id:
                query = query.filter(asignatura_id=subject_id)
            if start_date:
                query = query.filter(fecha__gte=start_date)
            if end_date:
                query = query.filter(fecha__lte=end_date)
            return query
        except Exception as e:
            raise Exception(f"Error al obtener asistencias: {str(e)}")

    @staticmethod
    def get_subject_attendance(subject_id, date=None):
        """Obtiene los registros de asistencia de una asignatura"""
        try:
            query = Asistencia.objects.filter(asignatura_id=subject_id)
            if date:
                query = query.filter(fecha=date)
            return query
        except Exception as e:
            raise Exception(f"Error al obtener asistencias: {str(e)}")

    @staticmethod
    def get_attendance_records(subject_id=None, start_date=None, end_date=None):
        """Obtiene los registros de asistencia de las clases"""
        try:
            query = RegistroAsistencia.objects.all()
            if subject_id:
                query = query.filter(asignatura_id=subject_id)
            if start_date:
                query = query.filter(fecha__gte=start_date)
            if end_date:
                query = query.filter(fecha__lte=end_date)
            return query
        except Exception as e:
            raise Exception(f"Error al obtener registros de asistencia: {str(e)}")

    @staticmethod
    def update_attendance(attendance_id, estado=None, justificacion=None):
        """Actualiza un registro de asistencia"""
        try:
            with transaction.atomic():
                asistencia = Asistencia.objects.get(id=attendance_id)
                if estado:
                    asistencia.estado = estado
                if justificacion is not None:
                    asistencia.justificacion = justificacion
                asistencia.save()
                return asistencia
        except Asistencia.DoesNotExist:
            raise Exception("Registro de asistencia no encontrado")
        except Exception as e:
            raise Exception(f"Error al actualizar asistencia: {str(e)}") 