from django.db import transaction
from django.utils import timezone
from .models import Evento, Recordatorio

class CalendarService:
    @staticmethod
    def create_event(titulo, descripcion, tipo, fecha_inicio, fecha_fin, asignatura, creador, participantes=None):
        """Crea un nuevo evento"""
        try:
            with transaction.atomic():
                evento = Evento.objects.create(
                    titulo=titulo,
                    descripcion=descripcion,
                    tipo=tipo,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    asignatura=asignatura,
                    creador=creador
                )
                if participantes:
                    evento.participantes.set(participantes)
                return evento
        except Exception as e:
            raise Exception(f"Error al crear evento: {str(e)}")

    @staticmethod
    def create_reminder(evento, usuario, tiempo_antes):
        """Crea un nuevo recordatorio"""
        try:
            with transaction.atomic():
                recordatorio = Recordatorio.objects.create(
                    evento=evento,
                    usuario=usuario,
                    tiempo_antes=tiempo_antes
                )
                return recordatorio
        except Exception as e:
            raise Exception(f"Error al crear recordatorio: {str(e)}")

    @staticmethod
    def get_user_events(user_id, start_date=None, end_date=None, tipo=None):
        """Obtiene los eventos de un usuario"""
        try:
            query = Evento.objects.filter(
                models.Q(creador_id=user_id) |
                models.Q(participantes__id=user_id)
            ).distinct()
            
            if start_date:
                query = query.filter(fecha_inicio__gte=start_date)
            if end_date:
                query = query.filter(fecha_fin__lte=end_date)
            if tipo:
                query = query.filter(tipo=tipo)
                
            return query
        except Exception as e:
            raise Exception(f"Error al obtener eventos: {str(e)}")

    @staticmethod
    def get_subject_events(subject_id, start_date=None, end_date=None):
        """Obtiene los eventos de una asignatura"""
        try:
            query = Evento.objects.filter(asignatura_id=subject_id)
            if start_date:
                query = query.filter(fecha_inicio__gte=start_date)
            if end_date:
                query = query.filter(fecha_fin__lte=end_date)
            return query
        except Exception as e:
            raise Exception(f"Error al obtener eventos: {str(e)}")

    @staticmethod
    def get_pending_reminders():
        """Obtiene los recordatorios pendientes"""
        try:
            now = timezone.now()
            return Recordatorio.objects.filter(
                enviado=False,
                evento__fecha_inicio__gt=now
            )
        except Exception as e:
            raise Exception(f"Error al obtener recordatorios: {str(e)}")

    @staticmethod
    def mark_reminder_sent(reminder_id):
        """Marca un recordatorio como enviado"""
        try:
            with transaction.atomic():
                recordatorio = Recordatorio.objects.get(id=reminder_id)
                recordatorio.enviado = True
                recordatorio.save()
                return recordatorio
        except Recordatorio.DoesNotExist:
            raise Exception("Recordatorio no encontrado")
        except Exception as e:
            raise Exception(f"Error al marcar recordatorio: {str(e)}") 