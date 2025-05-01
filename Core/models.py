from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('profesor', 'Profesor'),
        ('estudiante', 'Estudiante'),
    )
    
    rol = models.CharField(max_length=20, choices=ROLES, default='estudiante')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    direccion = models.TextField(null=True, blank=True)

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    profesor = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'profesor'})
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

class EstudianteCurso(models.Model):
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'estudiante'})
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateField(auto_now_add=True)

class Calificacion(models.Model):
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'estudiante'})
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    nota = models.DecimalField(max_digits=4, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    comentario = models.TextField(null=True, blank=True)

