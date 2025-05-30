import os
import django
from datetime import date
import sys
# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from Core.models import (
    AuthUser, Usuario, Especialidad, Docente, Administrativo, Curso, Estudiante, EvaluacionBase, Asignatura, AsignaturaImpartida
)
# Crear usuario administrador
admin_auth_user, _ = AuthUser.objects.get_or_create(
    rut='20120767',
    defaults={
        'div': '3',
        'password': make_password('admin123'),
        'is_admin': True,
        'is_active': True
    }
)
admin_auth_user.is_admin = True
admin_auth_user.save()

admin_usuario, _ = Usuario.objects.get_or_create(
    rut='20120767',
    defaults={
        'nombre': 'Admin',
        'apellido_paterno': 'Sistema',
        'apellido_materno': 'GEM',
        'div': '3',
        'correo': 'admin@gem.cl',
        'telefono': '123456789',
        'direccion': 'Dirección Admin',
        'fecha_nacimiento': date(1990, 1, 1),
        'auth_user': admin_auth_user
    }
)

Administrativo.objects.get_or_create(
    usuario=admin_usuario,
    defaults={'rol': 'ADMINISTRADOR'}
)

print('✅ Usuario administrador creado exitosamente')
