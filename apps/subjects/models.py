from django.db import models
from apps.users.models import User
from apps.classes.models import Clase

class Asignatura(models.Model):
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=20)
    dia = models.CharField(max_length=20)
    horario = models.CharField(max_length=20)
    docente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='asignaturas_docente'
    )
    clase = models.ForeignKey(
        Clase,
        on_delete=models.CASCADE,
        related_name='asignaturas'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Asignatura'
        verbose_name_plural = 'Asignaturas'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.codigo}"

class Electivo(models.Model):
    nombre = models.CharField(max_length=200)
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='electivos'
    )
    profesor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='electivos_profesor'
    )
    sala = models.CharField(max_length=50)
    dia = models.CharField(max_length=20)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Electivo'
        verbose_name_plural = 'Electivos'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.asignatura}" 