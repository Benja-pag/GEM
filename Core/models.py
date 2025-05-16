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

# Modelo base que representa a cualquier tipo de usuario en el sistema
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

    def __str__(self):
        return f'Docente: {self.usuario} - Especialidad: {self.especialidad}'
# Modelo para estudiantes
class Estudiante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)  # Relación uno a uno con Usuario
    contacto_emergencia = models.CharField(max_length=100)  # Información de contacto en caso de emergencia

    def __str__(self):
        return f'Estudiante: {self.usuario}'  # Representación legible del objeto

class Asistencia(models.Model):
    ESTADOS = [
        ('ASISTIO', 'Asistió'),
        ('AUSENTE', 'Ausente'),
        ('JUSTIFICADO', 'Justificado'),
    ]

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)  # Relación con estudiante
    fecha = models.DateField()  # Fecha de la asistencia
    estado = models.CharField(max_length=12, choices=ESTADOS)  # Estado de la asistencia
    hora_registro = models.TimeField(auto_now_add=True)  # Hora en que se registró (opcional, con auto)

    class Meta:
        unique_together = ('estudiante', 'fecha')  # Evita duplicados por estudiante y fecha

    def __str__(self):
        return f'{self.estudiante.usuario} - {self.fecha} - {self.get_estado_display()}'

class Calendario(models.Model):
    TIPOS_EVENTO = [
        ('PRUEBA', 'Prueba'),
        ('ENTREGA', 'Entrega de trabajo'),
        ('REUNION', 'Reunión'),
        ('ACTIVIDAD', 'Actividad general'),
        ('MATERIAL', 'Material disponible'),
        ('OTRO', 'Otro'),
    ]

    titulo = models.CharField(max_length=100)  # Título del evento
    descripcion = models.TextField(blank=True, null=True)  # Descripción adicional (opcional)
    tipo_evento = models.CharField(max_length=20, choices=TIPOS_EVENTO)  # Tipo de evento
    fecha_inicio = models.DateTimeField()  # Fecha y hora de inicio
    fecha_fin = models.DateTimeField()  # Fecha y hora de fin (puede ser igual al inicio si es un evento corto)
    creado_en = models.DateTimeField(auto_now_add=True)  # Registro automático de la creación del evento

    def __str__(self):
        return f'{self.titulo} ({self.get_tipo_evento_display()}) - {self.fecha_inicio.strftime("%d/%m/%Y %H:%M")}'

class Foro(models.Model):
    titulo = models.CharField(max_length=150)  # Título del tema o pregunta
    contenido = models.TextField()  # Cuerpo del mensaje o publicación
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Usuario que creó la publicación
    fecha_publicacion = models.DateTimeField(auto_now_add=True)  # Fecha automática de publicación

    def __str__(self):
        return f'{self.titulo} - por {self.autor.nombre} {self.autor.apellido_paterno}'

class Nota(models.Model):
    TIPOS_EVALUACION = [
        ('PRUEBA', 'Prueba'),
        ('TAREA', 'Tarea'),
        ('PROYECTO', 'Proyecto'),
        ('EXAMEN', 'Examen'),
        ('OTRO', 'Otro'),
    ]

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)  # Estudiante evaluado
    docente = models.ForeignKey(Docente, on_delete=models.SET_NULL, null=True)  # Docente que evaluó
    tipo_evaluacion = models.CharField(max_length=20, choices=TIPOS_EVALUACION)  # Tipo de evaluación
    descripcion = models.CharField(max_length=255, blank=True, null=True)  # Detalle de la evaluación
    nota = models.DecimalField(max_digits=4, decimal_places=2)  # Nota (por ejemplo: 6.50)
    fecha_registro = models.DateField(auto_now_add=True)  # Fecha de ingreso de la nota

    def __str__(self):
        return f'{self.estudiante.usuario} - {self.tipo_evaluacion} - {self.nota}'

# -------------------------------------
# ASIGNATURAS, CLASES Y RELACIONES
# -------------------------------------

class Asignatura(models.Model):
    nombre = models.CharField(max_length=100, unique=True)  # Ej: Matemáticas, Historia
    descripcion = models.TextField(blank=True, null=True)  # Opcional

    def __str__(self):
        return self.nombre


class CursoAsignado(models.Model):
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)  # Asignatura base
    docente = models.ForeignKey(Docente, on_delete=models.PROTECT)  # Profesor a cargo
    dias = models.CharField(max_length=50)  # Ej: "Lunes, Miércoles"
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    sala = models.CharField(max_length=50, blank=True, null=True)  # Opcional: sala o aula

    def __str__(self):
        return f'{self.asignatura.nombre} - {self.docente.usuario.nombre}'


class Clase(models.Model):
    curso = models.ForeignKey(CursoAsignado, on_delete=models.CASCADE, related_name='clases', null=True)
    fecha = models.DateField()
    descripcion = models.TextField(blank=True, null=True)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.curso.asignatura.nombre} - {self.fecha}'

class EstudianteAsignatura(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    curso_asignado = models.ForeignKey(CursoAsignado, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('estudiante', 'curso_asignado')

    def __str__(self):
        return f'{self.estudiante.usuario} inscrito en {self.curso_asignado.asignatura.nombre}'
class Curso(models.Model):
    letra = models.CharField(max_length=3, unique=True)  # Por ejemplo: '1A', '2B', etc.

    def __str__(self):
        return self.letra