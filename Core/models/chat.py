from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class Foro(models.Model):
    titulo = models.CharField(max_length=200)  # Título del foro o tema
    asunto = models.CharField(max_length=200)  # Asunto o subtítulo
    contenido = models.TextField()  # Contenido del mensaje o tema
    autor = models.ForeignKey('Usuario', on_delete=models.CASCADE)  # Autor del mensaje, relacionado con Usuario
    fecha = models.DateField(auto_now_add=True)  # Fecha de creación (auto asignada)
    hora = models.TimeField(auto_now_add=True)  # Hora de creación (auto asignada)

    def __str__(self):
        return f'{self.titulo} - {self.autor}'

class MensajeAlumnoProfesor(models.Model):
    emisor = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='mensajes_enviados')
    receptores = models.ManyToManyField('Usuario', related_name='mensajes_recibidos')
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f'Mensaje de {self.emisor} - {self.titulo}'

class ChatGrupo(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre del grupo
    estudiantes = models.ManyToManyField('Estudiante', blank=True, related_name='chats_grupo')
    docentes = models.ManyToManyField('Docente', blank=True, related_name='chats_grupo')
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE, null=True, blank=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    hora_creacion = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
  