from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class Asignatura(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50)
    dia = models.CharField(max_length=15, choices=[
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
    ])
    horario = models.TimeField()
    docente = models.ForeignKey('Docente', on_delete=models.PROTECT)
    clase = models.ForeignKey('Clase', on_delete=models.PROTECT)

    class Meta:
        unique_together = ('docente', 'dia', 'horario')  # Restricción para evitar superposición de horario por docente

    def __str__(self):
        return f'{self.nombre} ({self.codigo}) - {self.dia} {self.horario} - {self.docente} - {self.clase}'
    
class Clase(models.Model):
    nombre = models.CharField(max_length=100)
    profesor_jefe = models.ForeignKey('Docente', on_delete=models.SET_NULL, null=True, blank=True, related_name='clases_jefe')
    sala = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.nombre
    

class ClaseAsignatura(models.Model):
    docente = models.ForeignKey('Docente', on_delete=models.CASCADE)
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    dia = models.CharField(max_length=10)  # Por ejemplo: "lunes", "martes", etc.
    curso = models.CharField(max_length=50)  # Por ejemplo: "1 medio A"

    class Meta:
        unique_together = ('docente', 'dia', 'hora_inicio', 'hora_fin', 'curso')

    def __str__(self):
        return f'{self.docente} - {self.asignatura} - {self.dia} {self.hora_inicio}-{self.hora_fin} - {self.curso}'



class Electivo(models.Model):
    nombre = models.CharField(max_length=100)
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE)
    profesor = models.ForeignKey('Docente', on_delete=models.CASCADE)
    sala = models.CharField(max_length=50)
    dia = models.CharField(max_length=15, choices=[
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
    ])
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        unique_together = ('profesor', 'dia', 'hora_inicio', 'hora_fin')

    def __str__(self):
        return f'{self.nombre} ({self.asignatura.nombre}) - {self.dia} {self.hora_inicio}-{self.hora_fin}'


