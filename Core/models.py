from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class AuthUserManager(BaseUserManager):
    def create_user(self, rut, div, password=None):
        if not rut:
            raise ValueError('El RUT es obligatorio')
        if not div:
            raise ValueError('El dígito verificador es obligatorio')
        user = self.model(rut=rut, div=div)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, rut, div, password=None):
        user = self.create_user(rut=rut, div=div, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class AuthUser(AbstractBaseUser, PermissionsMixin):
    rut = models.CharField(max_length=20, unique=True)
    div = models.CharField(max_length=1)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['div']

    objects = AuthUserManager()

    def __str__(self):
        return f"{self.rut}-{self.div}"

    def get_full_name(self):
        return f"{self.rut}-{self.div}"

    def get_short_name(self):
        return self.rut

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

# Clase usuarios #
class Usuario(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre del usuario
    apellido_paterno = models.CharField(max_length=100)  # Apellido paterno
    apellido_materno = models.CharField(max_length=100)  # Apellido materno
    rut = models.CharField(max_length=10, unique=True)  # RUT sin dígito verificador, único por usuario
    div = models.CharField(max_length=1)  # Dígito verificador del RUT
    correo = models.EmailField(unique=True)  # Correo electrónico único
    telefono = models.CharField(max_length=15)  # Teléfono de contacto
    direccion = models.TextField()  # Dirección física del usuario
    fecha_nacimiento = models.DateField()  # Fecha de nacimiento del usuario
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación del registro (autoasignado)
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, null=True, blank=True)
    activador = models.BooleanField(default=True)  # Estado de activación de la cuenta

    def __str__(self):
        return f'{self.nombre} {self.apellido_paterno}'  # Representación legible del objeto

# Modelo para administrativos, incluyendo administradores máximos
class Administrativo(models.Model):
    # Definimos los roles disponibles para el administrativo
    ROLES = [
        ('ADMINISTRADOR', 'Administrador Máximo'),  # Rol para el administrador del sistema
        ('ADMINISTRATIVO', 'Administrativo'),       # Rol para personal administrativo regular
    ]
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)  # Relación uno a uno con Usuario
    rol = models.CharField(max_length=15, choices=ROLES)  # Campo para definir el rol

    def __str__(self):
        # Retorna el nombre del usuario con el rol legible (no la clave)
        return f'{self.usuario} - {self.get_rol_display()}'

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# Modelo para docentes
class Docente(models.Model):
    usuario = models.OneToOneField('Usuario', on_delete=models.CASCADE)
    especialidad = models.ForeignKey('Especialidad', on_delete=models.PROTECT, null=True, blank=True)  # ID de "Ninguna"
    es_profesor_jefe = models.BooleanField(default=False)  # Por defecto no es profesor jefe

    def __str__(self):
        return f'Docente: {self.usuario} - Especialidad: {self.especialidad}'

class Estudiante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    contacto_emergencia = models.CharField(max_length=100)
    clase = models.ForeignKey('Clase', on_delete=models.SET_NULL, null=True, blank=True, related_name='estudiantes')

    def __str__(self):
        return f'Estudiante: {self.usuario}'

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

class Nota(models.Model):
    TIPO_EVALUACION_CHOICES = [
        ('Prueba', 'Prueba'),
        ('Tarea', 'Tarea'),
        ('Examen', 'Examen'),
        ('Proyecto', 'Proyecto'),
        # Puedes agregar más tipos de evaluación si quieres
    ]

    tipo_evaluacion = models.CharField(max_length=20, choices=TIPO_EVALUACION_CHOICES)
    estudiante = models.ForeignKey('Estudiante', on_delete=models.CASCADE)
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE)
    nota = models.DecimalField(max_digits=5, decimal_places=2)  # Nota obtenida (por ejemplo, 61.00)
    puntaje_obtenido = models.DecimalField(max_digits=5, decimal_places=2)  # Puntaje real obtenido (37.00)
    puntaje_total = models.DecimalField(max_digits=5, decimal_places=2)  # Puntaje máximo posible (42.00)
    fecha = models.DateField()

    def __str__(self):
        return f'{self.tipo_evaluacion} - {self.estudiante} - {self.asignatura} - Nota: {self.nota}'

class Asistencia(models.Model):
    fecha = models.DateField()
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE)
    estudiante = models.ForeignKey('Estudiante', on_delete=models.CASCADE)
    asistencia = models.BooleanField()  # True = presente (sí), False = ausente (no)

    def __str__(self):
        estado = 'Presente' if self.asistencia else 'Ausente'
        return f'{self.fecha} - {self.asignatura} - {self.estudiante} - {estado}'

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

class CalendarioClase(models.Model):
    nombre_actividad = models.CharField(max_length=100)  # Nombre de la actividad, e.g., "Prueba"
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE)  # Relación con Asignatura
    descripcion = models.TextField(blank=True, null=True)  # Descripción de la actividad
    materiales = models.TextField(blank=True, null=True)  # Materiales generales (texto libre)
    lista_materiales = models.JSONField(blank=True, null=True)  # Lista estructurada de materiales, opcional
    fecha = models.DateField(blank=True, null=True)  # Fecha de la actividad
    hora = models.TimeField(blank=True, null=True)  # Hora de la actividad

    def __str__(self):
        return f'{self.nombre_actividad} - {self.asignatura} ({self.fecha} {self.hora})'
    
class CalendarioColegio(models.Model):
    nombre_actividad = models.CharField(max_length=100)  # Nombre de la actividad
    descripcion = models.TextField(blank=True, null=True)  # Descripción de la actividad
    encargado = models.CharField(max_length=100)  # Persona responsable de la actividad
    ubicacion = models.CharField(max_length=100)  # Lugar donde se realiza la actividad
    fecha = models.DateField()  # Fecha de la actividad
    hora = models.TimeField()  # Hora de la actividad

    def __str__(self):
        return f'{self.nombre_actividad} - {self.fecha} {self.hora}'

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
    
class Clase(models.Model):
    nombre = models.CharField(max_length=100)
    profesor_jefe = models.ForeignKey('Docente', on_delete=models.SET_NULL, null=True, blank=True, related_name='clases_jefe')
    sala = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.nombre
    
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

class InscripcionElectivo(models.Model):
    estudiante = models.ForeignKey('Estudiante', on_delete=models.CASCADE, related_name='electivos')
    electivo = models.ForeignKey('Electivo', on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('estudiante', 'electivo')  # Evita inscripciones duplicadas

    def __str__(self):
        return f'{self.estudiante} inscrito en {self.electivo}'
