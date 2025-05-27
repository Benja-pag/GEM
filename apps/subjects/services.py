from django.db import transaction
from .models import Asignatura, Electivo

class ServicioAsignatura:
    @staticmethod
    def crear_asignatura(nombre, codigo, dia, horario, docente_id, clase_id):
        """Crea una nueva asignatura"""
        try:
            with transaction.atomic():
                asignatura = Asignatura.objects.create(
                    nombre=nombre,
                    codigo=codigo,
                    dia=dia,
                    horario=horario,
                    docente_id=docente_id,
                    clase_id=clase_id
                )
                return asignatura
        except Exception as e:
            raise Exception(f"Error al crear asignatura: {str(e)}")

    @staticmethod
    def crear_electivo(nombre, asignatura_id, profesor_id, sala, dia, hora_inicio, hora_fin):
        """Crea un nuevo electivo"""
        try:
            with transaction.atomic():
                electivo = Electivo.objects.create(
                    nombre=nombre,
                    asignatura_id=asignatura_id,
                    profesor_id=profesor_id,
                    sala=sala,
                    dia=dia,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin
                )
                return electivo
        except Exception as e:
            raise Exception(f"Error al crear electivo: {str(e)}")

    @staticmethod
    def actualizar_asignatura(asignatura_id, **kwargs):
        """Actualiza una asignatura existente"""
        try:
            asignatura = Asignatura.objects.get(id=asignatura_id)
            for key, value in kwargs.items():
                setattr(asignatura, key, value)
            asignatura.save()
            return asignatura
        except Asignatura.DoesNotExist:
            raise Exception("Asignatura no encontrada")

    @staticmethod
    def obtener_asignaturas_docente(docente_id):
        """Obtiene todas las asignaturas de un docente"""
        return Asignatura.objects.filter(docente_id=docente_id)

    @staticmethod
    def obtener_asignaturas_clase(clase_id):
        """Obtiene todas las asignaturas de una clase"""
        return Asignatura.objects.filter(clase_id=clase_id)

    @staticmethod
    def obtener_electivos_profesor(profesor_id):
        """Obtiene todos los electivos de un profesor"""
        return Electivo.objects.filter(profesor_id=profesor_id)

    @staticmethod
    def obtener_electivos_asignatura(asignatura_id):
        """Obtiene todos los electivos de una asignatura"""
        return Electivo.objects.filter(asignatura_id=asignatura_id) 