from django.db import models
from apps.users.models import User
from apps.subjects.models import Asignatura

class Asistencia(models.Model):
    ESTADO_CHOICES = [
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
        ('justificado', 'Justificado'),
        ('tardanza', 'Tardanza'),
    ]

    alumno = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='asistencias'
    )
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='asistencias'
    )
    fecha = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    justificacion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        ordering = ['-fecha']
        unique_together = ['alumno', 'asignatura', 'fecha']

    def __str__(self):
        return f"{self.alumno} - {self.asignatura} - {self.fecha} - {self.estado}"

class RegistroAsistencia(models.Model):
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='registros_asistencia'
    )
    fecha = models.DateField()
    profesor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='registros_asistencia'
    )
    observaciones = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Registro de Asistencia'
        verbose_name_plural = 'Registros de Asistencia'
        ordering = ['-fecha']
        unique_together = ['asignatura', 'fecha']

    def __str__(self):
        return f"{self.asignatura} - {self.fecha}" 