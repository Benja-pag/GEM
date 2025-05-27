from django.db import models
from apps.users.models import User
from apps.subjects.models import Asignatura

class Calificacion(models.Model):
    alumno = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='calificaciones'
    )
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='calificaciones'
    )
    nota = models.DecimalField(max_digits=4, decimal_places=2)
    fecha = models.DateField()
    tipo = models.CharField(max_length=50)  # Examen, Tarea, Proyecto, etc.
    comentario = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.alumno} - {self.asignatura} - {self.nota}"

class Promedio(models.Model):
    alumno = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='promedios'
    )
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='promedios'
    )
    promedio = models.DecimalField(max_digits=4, decimal_places=2)
    periodo = models.CharField(max_length=50)  # Primer Semestre, Segundo Semestre, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Promedio'
        verbose_name_plural = 'Promedios'
        ordering = ['-periodo']

    def __str__(self):
        return f"{self.alumno} - {self.asignatura} - {self.promedio}" 