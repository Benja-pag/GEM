from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from django.db import models

# Evaluaciones Base: Plantillas generales por asignatura o tipo
class EvaluacionBase(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE, related_name='evaluaciones_base')
    ponderacion = models.DecimalField(max_digits=5, decimal_places=2, help_text="Porcentaje que representa esta evaluación (Ej: 20.00)")
    
    def __str__(self):
        return f'{self.nombre} - {self.asignatura.nombre}'


# Evaluaciones específicas aplicadas en una clase
class Evaluacion(models.Model):
    evaluacion_base = models.ForeignKey('EvaluacionBase', on_delete=models.CASCADE, related_name='evaluaciones')
    clase = models.ForeignKey('Clase', on_delete=models.CASCADE, related_name='evaluaciones')
    fecha = models.DateField()
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.evaluacion_base.nombre} - {self.clase} ({self.fecha})'


# Notas asignadas a cada estudiante para una evaluación
class AlumnoEvaluacion(models.Model):
    estudiante = models.ForeignKey('Estudiante', on_delete=models.CASCADE, related_name='notas')
    evaluacion = models.ForeignKey('Evaluacion', on_delete=models.CASCADE, related_name='resultados')
    nota = models.DecimalField(max_digits=4, decimal_places=2, help_text='Nota del estudiante (Ej: 6.50)')
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('estudiante', 'evaluacion')

    def __str__(self):
        return f'{self.estudiante.usuario} - {self.evaluacion.evaluacion_base.nombre}: {self.nota}'
