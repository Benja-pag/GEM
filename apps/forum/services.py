from django.db import transaction
from django.utils import timezone
from .models import Tema, Comentario, Reaccion

class ForumService:
    @staticmethod
    def create_tema(titulo, descripcion, asignatura, creador):
        """Crea un nuevo tema en el foro."""
        with transaction.atomic():
            tema = Tema.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                asignatura=asignatura,
                creador=creador
            )
            tema.participantes.add(creador)
            return tema

    @staticmethod
    def create_comentario(tema, autor, contenido):
        """Crea un nuevo comentario en un tema."""
        with transaction.atomic():
            comentario = Comentario.objects.create(
                tema=tema,
                autor=autor,
                contenido=contenido
            )
            tema.participantes.add(autor)
            return comentario

    @staticmethod
    def add_reaccion(comentario, usuario, tipo):
        """Añade o actualiza una reacción a un comentario."""
        with transaction.atomic():
            reaccion, created = Reaccion.objects.update_or_create(
                comentario=comentario,
                usuario=usuario,
                defaults={'tipo': tipo}
            )
            return reaccion

    @staticmethod
    def get_temas_activos(asignatura=None):
        """Obtiene los temas activos, opcionalmente filtrados por asignatura."""
        queryset = Tema.objects.filter(activo=True)
        if asignatura:
            queryset = queryset.filter(asignatura=asignatura)
        return queryset

    @staticmethod
    def get_comentarios_tema(tema):
        """Obtiene todos los comentarios de un tema."""
        return Comentario.objects.filter(tema=tema)

    @staticmethod
    def get_reacciones_comentario(comentario):
        """Obtiene todas las reacciones de un comentario."""
        return Reaccion.objects.filter(comentario=comentario)

    @staticmethod
    def close_tema(tema):
        """Cierra un tema del foro."""
        with transaction.atomic():
            tema.activo = False
            tema.save()
            return tema 