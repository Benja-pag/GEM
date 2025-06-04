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
    ACTIVIDAD_CHOICES = [
        ('Clase', 'Clase'),
        ('Recreo', 'Recreo'),
        ('Almuerzo', 'Almuerzo'),
    ]

    DIA_CHOICES = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
    ]

    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='horarios')
    asignatura_impartida = models.ForeignKey('AsignaturaImpartida', on_delete=models.CASCADE, null=True, blank=True)
    actividad = models.CharField(max_length=10, choices=ACTIVIDAD_CHOICES)
    dia = models.CharField(max_length=10, choices=DIA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        unique_together = [
            ('curso', 'dia', 'hora_inicio'),  # No puede haber dos actividades al mismo tiempo para un curso
        ]

    def __str__(self):
        if self.actividad == 'Clase':
            return f'{self.curso} - {self.asignatura_impartida.codigo} - {self.actividad} - {self.dia} ({self.hora_inicio}-{self.hora_fin})'
        return f'{self.curso} - {self.actividad} - {self.dia} ({self.hora_inicio}-{self.hora_fin})'
