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


class Usuario(models.Model):
    rut = models.CharField(max_length=20, unique=True)
    div = models.CharField(max_length=1)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    fecha_nacimiento = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, null=True, blank=True)
    activador = models.BooleanField(default=True)
    password = models.CharField(max_length=128, null=True)

    def __str__(self):
        return f'{self.nombre} {self.apellido_paterno}'  # Representación legible del objeto


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


class Docente(models.Model):
    usuario = models.OneToOneField('Usuario', on_delete=models.CASCADE)
    especialidad = models.ForeignKey('Especialidad', on_delete=models.PROTECT, null=True, blank=True)  # ID de "Ninguna"
    es_profesor_jefe = models.BooleanField(default=False)  # Por defecto no es profesor jefe

    def __str__(self):
        return f'Docente: {self.usuario} - Especialidad: {self.especialidad}'

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Estudiante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    contacto_emergencia = models.CharField(max_length=100)
    clase = models.ForeignKey('Clase', on_delete=models.SET_NULL, null=True, blank=True, related_name='estudiantes')

    def __str__(self):
        return f'Estudiante: {self.usuario}'
