from django.db import models
from apps.users.models import User

class Clase(models.Model):
    nombre = models.CharField(max_length=100)
    curso = models.CharField(max_length=50)
    profesor_jefe = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='clases_jefe'
    )
    alumnos = models.ManyToManyField(
        User,
        related_name='clases_alumno'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Clase'
        verbose_name_plural = 'Clases'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.curso}"

class Sala(models.Model):
    nombre = models.CharField(max_length=50)
    capacidad = models.IntegerField()
    ubicacion = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sala'
        verbose_name_plural = 'Salas'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - Capacidad: {self.capacidad}" 