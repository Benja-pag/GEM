from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class Nota(models.Model):
    TIPO_EVALUACION_CHOICES = [
        ('Prueba', 'Prueba'),
        ('Tarea', 'Tarea'),
        ('Examen', 'Examen'),
        ('Proyecto', 'Proyecto'),
        # Puedes agregar más tipos de evaluación si quieres
    ]

    tipo_evaluacion = models.CharField(max_length=20, choices=TIPO_EVALUACION_CHOICES)
    estudiante = models.ForeignKey('Estudiante', on_delete=models.CASCADE)
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE)
    nota = models.DecimalField(max_digits=5, decimal_places=2)  # Nota obtenida (por ejemplo, 61.00)
    puntaje_obtenido = models.DecimalField(max_digits=5, decimal_places=2)  # Puntaje real obtenido (37.00)
    puntaje_total = models.DecimalField(max_digits=5, decimal_places=2)  # Puntaje máximo posible (42.00)
    fecha = models.DateField()

    def __str__(self):
        return f'{self.tipo_evaluacion} - {self.estudiante} - {self.asignatura} - Nota: {self.nota}'

class Asistencia(models.Model):
    fecha = models.DateField()
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE)
    estudiante = models.ForeignKey('Estudiante', on_delete=models.CASCADE)
    asistencia = models.BooleanField()  # True = presente (sí), False = ausente (no)

    def __str__(self):
        estado = 'Presente' if self.asistencia else 'Ausente'
        return f'{self.fecha} - {self.asignatura} - {self.estudiante} - {estado}'
