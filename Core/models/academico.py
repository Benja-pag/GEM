from django.db import models
from django.utils import timezone

class MaterialClase(models.Model):
    clase = models.ForeignKey('Clase', on_delete=models.CASCADE, related_name='materiales')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    archivo = models.FileField(upload_to='materiales_clase/', null=True, blank=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.titulo} - {self.clase}'

class Tarea(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_CURSO', 'En Curso'),
        ('ENTREGADA', 'Entregada'),
        ('CALIFICADA', 'Calificada')
    ]
    
    asignatura_impartida = models.ForeignKey('AsignaturaImpartida', on_delete=models.CASCADE, related_name='tareas')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')

    def __str__(self):
        return f'{self.titulo} - {self.asignatura_impartida}'

class AnotacionCurso(models.Model):
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='anotaciones')
    autor = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    es_publica = models.BooleanField(default=True)

    def __str__(self):
        return f'Anotación de {self.autor} en {self.curso}'

class ObjetivoAsignatura(models.Model):
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE, related_name='objetivos')
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    completado = models.BooleanField(default=False)

    def __str__(self):
        return f'Objetivo de {self.asignatura}'

class RecursoAsignatura(models.Model):
    TIPO_CHOICES = [
        ('DOCUMENTO', 'Documento'),
        ('VIDEO', 'Video'),
        ('ENLACE', 'Enlace'),
        ('OTRO', 'Otro')
    ]
    
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE, related_name='recursos')
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    url = models.URLField(blank=True, null=True)
    archivo = models.FileField(upload_to='recursos_asignatura/', null=True, blank=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.titulo} - {self.asignatura}' 