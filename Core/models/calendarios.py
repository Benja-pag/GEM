from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class CalendarioClase(models.Model):
    nombre_actividad = models.CharField(max_length=100)  # Nombre de la actividad, e.g., "Prueba"
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE)  # Relación con Asignatura
    descripcion = models.TextField(blank=True, null=True)  # Descripción de la actividad
    materiales = models.TextField(blank=True, null=True)  # Materiales generales (texto libre)
    lista_materiales = models.JSONField(blank=True, null=True)  # Lista estructurada de materiales, opcional
    fecha = models.DateField(blank=True, null=True)  # Fecha de la actividad
    hora = models.TimeField(blank=True, null=True)  # Hora de la actividad

    def __str__(self):
        return f'{self.nombre_actividad} - {self.asignatura} ({self.fecha} {self.hora})'
    
class CalendarioColegio(models.Model):
    nombre_actividad = models.CharField(max_length=100)  # Nombre de la actividad
    descripcion = models.TextField(blank=True, null=True)  # Descripción de la actividad
    encargado = models.CharField(max_length=100)  # Persona responsable de la actividad
    ubicacion = models.CharField(max_length=100)  # Lugar donde se realiza la actividad
    fecha = models.DateField()  # Fecha de la actividad
    hora = models.TimeField()  # Hora de la actividad

    def __str__(self):
        return f'{self.nombre_actividad} - {self.fecha} {self.hora}'
