from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .models import Estudiante, Docente

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


# # Modelo base que representa a cualquier tipo de usuario en el sistema
# class Usuario(models.Model):
#     nombre = models.CharField(max_length=100)  # Nombre del usuario
#     apellido_paterno = models.CharField(max_length=100)  # Apellido paterno
#     apellido_materno = models.CharField(max_length=100)  # Apellido materno
#     rut = models.CharField(max_length=10, unique=True)  # RUT sin dígito verificador, único por usuario
#     div = models.CharField(max_length=1)  # Dígito verificador del RUT
#     correo = models.EmailField(unique=True)  # Correo electrónico único
#     telefono = models.CharField(max_length=15)  # Teléfono de contacto
#     direccion = models.TextField()  # Dirección física del usuario
#     fecha_nacimiento = models.DateField()  # Fecha de nacimiento del usuario
#     fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación del registro (autoasignado)

#     def __str__(self):
#         return f'{self.nombre} {self.apellido_paterno}'  # Representación legible del objeto

# # Modelo para administrativos, incluyendo administradores máximos
# class Administrativo(models.Model):
#     # Definimos los roles disponibles para el administrativo
#     ROLES = [
#         ('ADMINISTRADOR', 'Administrador Máximo'),  # Rol para el administrador del sistema
#         ('ADMINISTRATIVO', 'Administrativo'),       # Rol para personal administrativo regular
#     ]
#     usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)  # Relación uno a uno con Usuario
#     rol = models.CharField(max_length=15, choices=ROLES)  # Campo para definir el rol

#     def __str__(self):
#         # Retorna el nombre del usuario con el rol legible (no la clave)
#         return f'{self.usuario} - {self.get_rol_display()}'

# # Modelo para docentes
# class Docente(models.Model):
#     usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)  # Relación uno a uno con Usuario

#     def __str__(self):
#         return f'Docente: {self.usuario}'  # Representación legible del objeto

# # Modelo para estudiantes
# class Estudiante(models.Model):
#     usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)  # Relación uno a uno con Usuario
#     contacto_emergencia = models.CharField(max_length=100)  # Información de contacto en caso de emergencia

#     def __str__(self):
#         return f'Estudiante: {self.usuario}'  # Representación legible del objeto

# class Asistencia(models.Model):
#     ESTADOS = [
#         ('ASISTIO', 'Asistió'),
#         ('AUSENTE', 'Ausente'),
#         ('JUSTIFICADO', 'Justificado'),
#     ]

#     estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)  # Relación con estudiante
#     fecha = models.DateField()  # Fecha de la asistencia
#     estado = models.CharField(max_length=12, choices=ESTADOS)  # Estado de la asistencia
#     hora_registro = models.TimeField(auto_now_add=True)  # Hora en que se registró (opcional, con auto)

#     class Meta:
#         unique_together = ('estudiante', 'fecha')  # Evita duplicados por estudiante y fecha

#     def __str__(self):
#         return f'{self.estudiante.usuario} - {self.fecha} - {self.get_estado_display()}'

# class Calendario(models.Model):
#     TIPOS_EVENTO = [
#         ('PRUEBA', 'Prueba'),
#         ('ENTREGA', 'Entrega de trabajo'),
#         ('REUNION', 'Reunión'),
#         ('ACTIVIDAD', 'Actividad general'),
#         ('MATERIAL', 'Material disponible'),
#         ('OTRO', 'Otro'),
#     ]

#     titulo = models.CharField(max_length=100)  # Título del evento
#     descripcion = models.TextField(blank=True, null=True)  # Descripción adicional (opcional)
#     tipo_evento = models.CharField(max_length=20, choices=TIPOS_EVENTO)  # Tipo de evento
#     fecha_inicio = models.DateTimeField()  # Fecha y hora de inicio
#     fecha_fin = models.DateTimeField()  # Fecha y hora de fin (puede ser igual al inicio si es un evento corto)
#     creado_en = models.DateTimeField(auto_now_add=True)  # Registro automático de la creación del evento

#     def __str__(self):
#         return f'{self.titulo} ({self.get_tipo_evento_display()}) - {self.fecha_inicio.strftime("%d/%m/%Y %H:%M")}'

# class Clase(models.Model):
#     docente = models.ForeignKey(Docente, on_delete=models.CASCADE)  # Quién imparte la clase
#     titulo = models.CharField(max_length=100)  # Título de la clase
#     descripcion = models.TextField(blank=True, null=True)  # Detalle de contenido o temas (opcional)
#     fecha = models.DateField()  # Día en que se realiza la clase
#     hora_inicio = models.TimeField()  # Hora de inicio
#     hora_fin = models.TimeField()  # Hora de término
#     creado_en = models.DateTimeField(auto_now_add=True)  # Fecha en que se registró la clase

#     def __str__(self):
#         return f'{self.titulo} - {self.fecha} ({self.docente.usuario.nombre})'

# class Foro(models.Model):
#     titulo = models.CharField(max_length=150)  # Título del tema o pregunta
#     contenido = models.TextField()  # Cuerpo del mensaje o publicación
#     autor = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Usuario que creó la publicación
#     fecha_publicacion = models.DateTimeField(auto_now_add=True)  # Fecha automática de publicación

#     def __str__(self):
#         return f'{self.titulo} - por {self.autor.nombre} {self.autor.apellido_paterno}'

# class Nota(models.Model):
#     TIPOS_EVALUACION = [
#         ('PRUEBA', 'Prueba'),
#         ('TAREA', 'Tarea'),
#         ('PROYECTO', 'Proyecto'),
#         ('EXAMEN', 'Examen'),
#         ('OTRO', 'Otro'),
#     ]

#     estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)  # Estudiante evaluado
#     docente = models.ForeignKey(Docente, on_delete=models.SET_NULL, null=True)  # Docente que evaluó
#     tipo_evaluacion = models.CharField(max_length=20, choices=TIPOS_EVALUACION)  # Tipo de evaluación
#     descripcion = models.CharField(max_length=255, blank=True, null=True)  # Detalle de la evaluación
#     nota = models.DecimalField(max_digits=4, decimal_places=2)  # Nota (por ejemplo: 6.50)
#     fecha_registro = models.DateField(auto_now_add=True)  # Fecha de ingreso de la nota

#     def __str__(self):
#         return f'{self.estudiante.usuario} - {self.tipo_evaluacion} - {self.nota}'