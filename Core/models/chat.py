from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


# Foro principal creado por un usuario
class Foro(models.Model):
    titulo = models.CharField(max_length=200)
    asunto = models.CharField(max_length=200)
    contenido = models.TextField()
    autor = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.titulo} - {self.autor}'


# Mensajes o respuestas dentro de un foro específico
class MensajeForo(models.Model):
    foro = models.ForeignKey('Foro', on_delete=models.CASCADE, related_name='mensajes')
    autor = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Respuesta de {self.autor} en {self.foro.titulo}'


# Chat individual por clase (por ejemplo, 2B - Matemáticas)
class ChatClase(models.Model):
    clase = models.OneToOneField('Clase', on_delete=models.CASCADE, related_name='chat')
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f'Chat de Clase: {self.nombre}'


# Chat grupal general entre usuarios (grupos de estudio, electivos, etc.)
class ChatGrupo(models.Model):
    nombre = models.CharField(max_length=100)
    participantes = models.ManyToManyField('Usuario', related_name='chats_grupales')

    def __str__(self):
        return self.nombre


# Mensajes enviados dentro de los chats (ya sea por clase o grupo)
class MensajeChat(models.Model):
    autor = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='mensajes_chat')
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    chat_clase = models.ForeignKey('ChatClase', on_delete=models.CASCADE, related_name='mensajes', null=True, blank=True)
    chat_grupo = models.ForeignKey('ChatGrupo', on_delete=models.CASCADE, related_name='mensajes', null=True, blank=True)
    es_publico = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        if self.chat_clase:
            return f'Mensaje de {self.autor} en clase {self.chat_clase}'
        elif self.chat_grupo:
            return f'Mensaje de {self.autor} en grupo {self.chat_grupo}'
        else:
            return f'Mensaje público de {self.autor}'


# Foro específico para una asignatura
class ForoAsignatura(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    autor = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    asignatura = models.ForeignKey('AsignaturaImpartida', on_delete=models.CASCADE, related_name='foros')
    fecha = models.DateTimeField(auto_now_add=True)
    es_anuncio = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.titulo} - {self.asignatura.codigo}'

    class Meta:
        ordering = ['-fecha']


# Mensajes o respuestas dentro de un foro de asignatura
class MensajeForoAsignatura(models.Model):
    foro = models.ForeignKey('ForoAsignatura', on_delete=models.CASCADE, related_name='mensajes')
    autor = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Respuesta de {self.autor} en {self.foro.titulo}'

    class Meta:
        ordering = ['fecha']
