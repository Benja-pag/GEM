from django.db import models
from django.conf import settings

class Comunicacion(models.Model):
    """
    Representa una comunicación oficial, como un anuncio o circular.
    """
    asunto = models.CharField(max_length=255)
    contenido = models.TextField()
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comunicaciones_enviadas'
    )
    destinatarios_usuarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='comunicaciones_recibidas',
        blank=True
    )
    destinatarios_cursos = models.ManyToManyField(
        'Curso',
        related_name='comunicaciones',
        blank=True
    )
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido_por = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='comunicaciones_leidas',
        blank=True,
        help_text="Usuarios que han leído la comunicación"
    )

    def __str__(self):
        return self.asunto

    class Meta:
        verbose_name = "Comunicación"
        verbose_name_plural = "Comunicaciones"
        ordering = ['-fecha_envio']

def ruta_adjunto_comunicacion(instance, filename):
    """
    Genera la ruta de guardado para los archivos adjuntos de una comunicación.
    Ej: 'comunicaciones/adjuntos/comunicacion_5/archivo.pdf'
    """
    return f'comunicaciones/adjuntos/comunicacion_{instance.comunicacion.id}/{filename}'

class AdjuntoComunicacion(models.Model):
    """
    Representa un archivo adjunto en una comunicación.
    """
    comunicacion = models.ForeignKey(
        Comunicacion,
        on_delete=models.CASCADE,
        related_name='adjuntos'
    )
    archivo = models.FileField(upload_to=ruta_adjunto_comunicacion)
    nombre_archivo = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.nombre_archivo:
            self.nombre_archivo = self.archivo.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Adjunto "{self.nombre_archivo}" de la comunicación "{self.comunicacion.asunto}"'

    class Meta:
        verbose_name = "Adjunto de Comunicación"
        verbose_name_plural = "Adjuntos de Comunicaciones" 