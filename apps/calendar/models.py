from django.db import models
from apps.users.models import User
from apps.subjects.models import Asignatura

class Evento(models.Model):
    TIPO_CHOICES = [
        ('clase', 'Clase'),
        ('examen', 'Examen'),
        ('tarea', 'Tarea'),
        ('reunion', 'Reunión'),
        ('otro', 'Otro'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='eventos',
        null=True,
        blank=True
    )
    creador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='eventos_creados'
    )
    participantes = models.ManyToManyField(
        User,
        related_name='eventos_participantes',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['fecha_inicio']

    def __str__(self):
        return f"{self.titulo} - {self.fecha_inicio}"

class Recordatorio(models.Model):
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='recordatorios'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recordatorios'
    )
    tiempo_antes = models.IntegerField(help_text='Minutos antes del evento')
    enviado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Recordatorio'
        verbose_name_plural = 'Recordatorios'
        ordering = ['-created_at']

    def __str__(self):
        return f"Recordatorio para {self.evento.titulo} - {self.usuario}" 