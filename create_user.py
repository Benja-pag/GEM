# create_user.py

import os
import django
from datetime import date

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')  # Cambia 'GEM' si tu proyecto se llama distinto
django.setup()

# Ahora se pueden importar los modelos
from Core.models import AuthUser, Usuario, Administrativo

# Crear AuthUser
auth_user = AuthUser.objects.create_user(
    rut='20120767',
    div='3',
    password='admin123'
)
auth_user.is_admin = True
auth_user.save()

# Crear Usuario
usuario = Usuario.objects.create(
    nombre='Admin',
    apellido_paterno='Sistema',
    apellido_materno='GEM',
    rut='20120767',
    div='3',
    correo='admin@gem.cl',
    telefono='123456789',
    direccion='Dirección Admin',
    fecha_nacimiento=date(1990, 1, 1),
    auth_user=auth_user
)

# Crear Administrativo
admin = Administrativo.objects.create(
    usuario=usuario,
    rol='ADMINISTRADOR'
)

print('Usuario administrador creado exitosamente')
