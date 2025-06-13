from django.db import models
from django.utils import timezone

class ConfiguracionColegio(models.Model):
    nombre_colegio = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    ano_academico = models.PositiveIntegerField()
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración del Colegio'
        verbose_name_plural = 'Configuraciones del Colegio'

    def __str__(self):
        return f'{self.nombre_colegio} - {self.ano_academico}'

class LogActividad(models.Model):
    TIPO_CHOICES = [
        ('CREACION', 'Creación'),
        ('ACTUALIZACION', 'Actualización'),
        ('ELIMINACION', 'Eliminación'),
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
        ('OTRO', 'Otro')
    ]

    usuario = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    accion = models.CharField(max_length=200)
    fecha = models.DateTimeField(auto_now_add=True)
    detalles = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = 'Registro de Actividad'
        verbose_name_plural = 'Registros de Actividad'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.tipo} - {self.usuario} - {self.fecha}' 