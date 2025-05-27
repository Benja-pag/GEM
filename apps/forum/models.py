from django.db import models
from apps.users.models import User
from apps.subjects.models import Asignatura

class Tema(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='temas'
    )
    creador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='temas_creados'
    )
    participantes = models.ManyToManyField(
        User,
        related_name='temas_participantes',
        blank=True
    )
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tema'
        verbose_name_plural = 'Temas'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titulo} - {self.asignatura}"

class Comentario(models.Model):
    tema = models.ForeignKey(
        Tema,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    autor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    contenido = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['created_at']

    def __str__(self):
        return f"Comentario de {self.autor} en {self.tema}"

class Reaccion(models.Model):
    TIPO_CHOICES = [
        ('like', 'Me gusta'),
        ('dislike', 'No me gusta'),
        ('ayuda', 'Ayuda'),
    ]

    comentario = models.ForeignKey(
        Comentario,
        on_delete=models.CASCADE,
        related_name='reacciones'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reacciones'
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reacción'
        verbose_name_plural = 'Reacciones'
        unique_together = ['comentario', 'usuario']

    def __str__(self):
        return f"{self.usuario} - {self.tipo} en {self.comentario}" 