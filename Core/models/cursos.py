from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
#Tabla Asignatura#
class Asignatura(models.Model):
    NIVEL_CHOICES = [(i, f"{i}°") for i in range(1, 5)]  # 1° a 4°
    
    nombre = models.CharField(max_length=100)
    nivel = models.PositiveSmallIntegerField(choices=NIVEL_CHOICES)
    es_electivo = models.BooleanField(default=False, help_text="Marca si la asignatura es de tipo electivo")

    def __str__(self):
        return self.nombre

#Tabla Asignatura_impartida#
class AsignaturaImpartida(models.Model):
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE, related_name='imparticiones')
    docente = models.ForeignKey('Docente', on_delete=models.SET_NULL, null=True, related_name='asignaturas_impartidas')
    codigo = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9_-]+$',
                message='El código solo puede contener letras, números, guiones (-) y guiones bajos (_).'
            )
        ],
        help_text='Ej: MAT_101, BIO-2, HIS01'
    )

    def __str__(self):
        return f'{self.codigo} - {self.asignatura.nombre} - {self.docente.usuario.nombre} {self.docente.usuario.apellido_paterno}'
#Tabla Asignatura_inscrita#
class AsignaturaInscrita(models.Model):
    estudiante = models.ForeignKey('Estudiante', on_delete=models.CASCADE, related_name='asignaturas_inscritas')
    asignatura_impartida = models.ForeignKey('AsignaturaImpartida', on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(default=timezone.now)
    validada = models.BooleanField(default=False, help_text="Si la inscripción fue confirmada por el sistema o administración")

    class Meta:
        unique_together = ('estudiante', 'asignatura_impartida')

    def __str__(self):
        return f'{self.estudiante.usuario} inscrito en {self.asignatura_impartida.asignatura.nombre}'
#Tabla Clase#
class Clase(models.Model):
    DIAS_CHOICES = [
        ('LUNES', 'Lunes'),
        ('MARTES', 'Martes'),
        ('MIERCOLES', 'Miércoles'),
        ('JUEVES', 'Jueves'),
        ('VIERNES', 'Viernes'),
    ]

    SALA_CHOICES = [
        ('SALA_1', 'Sala 1'),
        ('SALA_2', 'Sala 2'),
        ('SALA_3', 'Sala 3'),
        ('SALA_4', 'Sala 4'),
        ('SALA_5', 'Sala 5'),
        ('SALA_6', 'Sala 6'),
        ('SALA_7', 'Sala 7'),
        ('SALA_8', 'Sala 8'),
        ('LAB_COMP', 'Laboratorio de Computación'),
        ('LAB_CIEN', 'Laboratorio de Ciencias'),
        ('GIMNASIO', 'Gimnasio'),
        ('BIBLIOTECA', 'Biblioteca'),
        ('AUDITORIO', 'Auditorio'),
    ]
    
    asignatura_impartida = models.ForeignKey('AsignaturaImpartida', on_delete=models.CASCADE, related_name='clases')
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='clases', null=True, blank=True, help_text='Opcional para asignaturas electivas donde se mezclan cursos')
    fecha = models.CharField(max_length=10, choices=DIAS_CHOICES)
    horario = models.CharField(max_length=100, help_text='Ej: 08:00-09:30')
    sala = models.CharField(max_length=20, choices=SALA_CHOICES, help_text='Sala donde se impartirá la clase')

    def __str__(self):
        curso_str = f' - {self.curso}' if self.curso else ''
        return f'{self.asignatura_impartida} - {self.fecha} - {self.sala}{curso_str}'

#Tabla Curso#
class Curso(models.Model):
    NIVEL_CHOICES = [(i, f"{i}°") for i in range(1, 5)]  # 1° a 4°
    LETRA_CHOICES = [(l, l) for l in ['A', 'B']]

    nivel = models.PositiveSmallIntegerField(choices=NIVEL_CHOICES)
    letra = models.CharField(max_length=1, choices=LETRA_CHOICES)
    
    class Meta:
        unique_together = ('nivel', 'letra')

    def __str__(self):
        return f"{self.nivel}°{self.letra}"  # Ej: "1A"

#Tabla Asistencia#
class Asistencia(models.Model):
    clase = models.ForeignKey('Clase', on_delete=models.CASCADE, related_name='asistencias', null=True, blank=True)
    estudiante = models.ForeignKey('Estudiante', on_delete=models.CASCADE, related_name='asistencias')
    presente = models.BooleanField(default=False)
    justificado = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('clase', 'estudiante')  # Un registro único por estudiante y clase

    def __str__(self):
        estado = "Presente" if self.presente else "Ausente"
        if self.justificado:
            estado += " (Justificado)"
        return f'{self.estudiante} - {self.clase} - {estado}'
