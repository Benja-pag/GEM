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

class HorarioCurso(models.Model):
    BLOQUE_CHOICES = [
        ('1', '08:00 - 08:45'),
        ('2', '08:45 - 09:30'),
        ('RECREO1', '09:30 - 09:45'),
        ('3', '09:45 - 10:30'),
        ('4', '10:30 - 11:15'),
        ('RECREO2', '11:15 - 11:30'),
        ('5', '11:30 - 12:15'),
        ('6', '12:15 - 13:00'),
        ('ALMUERZO', '13:00 - 13:45'),
        ('7', '13:45 - 14:30'),
        ('8', '14:30 - 15:15'),
        ('9', '15:15 - 16:00'),
    ]

    DIA_CHOICES = [
        ('LUNES', 'Lunes'),
        ('MARTES', 'Martes'),
        ('MIERCOLES', 'Miércoles'),
        ('JUEVES', 'Jueves'),
        ('VIERNES', 'Viernes'),
    ]

    ACTIVIDAD_CHOICES = [
        ('CLASE', 'Clase'),
        ('RECREO', 'Recreo'),
        ('ALMUERZO', 'Almuerzo'),
    ]

    bloque = models.CharField(max_length=8, choices=BLOQUE_CHOICES)
    dia = models.CharField(max_length=10, choices=DIA_CHOICES)
    actividad = models.CharField(max_length=8, choices=ACTIVIDAD_CHOICES)

    def __str__(self):
        return f'{self.dia} - {self.get_bloque_display()} - {self.actividad}'

    class Meta:
        unique_together = [('bloque', 'dia')]

    @property
    def es_viernes(self):
        return self.dia == 'VIERNES'

    @property
    def horario_valido(self):
        if self.es_viernes and self.bloque in ['7', '8', '9', 'ALMUERZO']:
            return False
        return True
