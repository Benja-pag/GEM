from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
#Tabla Asignatura#
class Asignatura(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
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
    horario = models.CharField(max_length=100, help_text='Ej: Lunes 08:00-09:30')

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
    asignatura_impartida = models.ForeignKey('AsignaturaImpartida', on_delete=models.CASCADE, related_name='clases')
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='clases')  # Relación con Curso
    fecha = models.DateField()
    horario = models.CharField(max_length=100, help_text='Ej: 08:00-09:30')
    contenido = models.TextField(blank=True, null=True, help_text='Temas tratados en esta clase')
    observaciones = models.TextField(blank=True, null=True)
    realizada = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.asignatura_impartida} - {self.curso} - {self.fecha}'

#Tabla Curso#
class Curso(models.Model):
    NIVEL_CHOICES = [(i, f"{i}°") for i in range(1, 5)]  # 1° a 4°
    LETRA_CHOICES = [(l, l) for l in ['A', 'B']]

    nivel = models.PositiveSmallIntegerField(choices=NIVEL_CHOICES)
    letra = models.CharField(max_length=1, choices=LETRA_CHOICES)
    
    class Meta:
        unique_together = ('nivel', 'letra')

    def __str__(self):
        return f"{self.nivel}{self.letra}"  # Ej: "1A"

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
