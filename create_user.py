import os
import django
<<<<<<< Updated upstream
from datetime import date

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

# Importación de modelos
from Core.models import AuthUser, Usuario, Administrativo, Docente, Estudiante

# ------------------------------------
# Crear usuario administrador
# ------------------------------------
admin_auth_user = AuthUser.objects.create_user(
    rut='20120767',
    div='3',
    password='admin123'
)
admin_auth_user.is_admin = True
admin_auth_user.save()

admin_usuario = Usuario.objects.create(
    nombre='Admin',
    apellido_paterno='Sistema',
    apellido_materno='GEM',
    rut='20120767',
    div='3',
    correo='admin@gem.cl',
    telefono='123456789',
    direccion='Dirección Admin',
    fecha_nacimiento=date(1990, 1, 1),
    auth_user=admin_auth_user
)

Administrativo.objects.create(
    usuario=admin_usuario,
    rol='ADMINISTRADOR'
)

print('✅ Usuario administrador creado exitosamente')

# ------------------------------------
# Crear docentes
# ------------------------------------
docentes_data = [
    {
        'rut': '12345678', 'div': '9',
        'nombre': 'Juan', 'apellido_paterno': 'Pérez', 'apellido_materno': 'López',
        'correo': 'juan.perez@gem.cl', 'telefono': '111111111',
        'direccion': 'Calle Falsa 123', 'fecha_nacimiento': date(1980, 5, 10)
    },
    {
        'rut': '23456789', 'div': '5',
        'nombre': 'María', 'apellido_paterno': 'González', 'apellido_materno': 'Ruiz',
        'correo': 'maria.gonzalez@gem.cl', 'telefono': '222222222',
        'direccion': 'Av. Siempre Viva 742', 'fecha_nacimiento': date(1985, 8, 20)
    }
]

for data in docentes_data:
    password = f"{data['nombre'][0]}{data['apellido_paterno']}".lower()
    auth_user = AuthUser.objects.create_user(
        rut=data['rut'],
        div=data['div'],
        password=password
    )
    usuario = Usuario.objects.create(
        nombre=data['nombre'],
        apellido_paterno=data['apellido_paterno'],
        apellido_materno=data['apellido_materno'],
        rut=data['rut'],
        div=data['div'],
        correo=data['correo'],
        telefono=data['telefono'],
        direccion=data['direccion'],
        fecha_nacimiento=data['fecha_nacimiento'],
        auth_user=auth_user
    )
    Docente.objects.create(usuario=usuario)
    print(f"✅ Docente {usuario.nombre} {usuario.apellido_paterno} creado con contraseña '{password}'")

# ------------------------------------
# Crear estudiantes
# ------------------------------------
estudiantes_data = [
    {
        'rut': '34567890', 'div': 'K',
        'nombre': 'Luis', 'apellido_paterno': 'Ramírez', 'apellido_materno': 'Soto',
        'correo': 'luis.ramirez@gem.cl', 'telefono': '333333333',
        'direccion': 'Pje. Los Robles 45', 'fecha_nacimiento': date(2008, 3, 15),
        'contacto_emergencia': 'Mamá: 999999999'
    },
    {
        'rut': '45678901', 'div': '1',
        'nombre': 'Ana', 'apellido_paterno': 'Castillo', 'apellido_materno': 'Vega',
        'correo': 'ana.castillo@gem.cl', 'telefono': '444444444',
        'direccion': 'Villa Las Flores 12', 'fecha_nacimiento': date(2009, 7, 5),
        'contacto_emergencia': 'Papá: 888888888'
    },
    {
        'rut': '56789012', 'div': '7',
        'nombre': 'Carlos', 'apellido_paterno': 'Muñoz', 'apellido_materno': 'Araya',
        'correo': 'carlos.munoz@gem.cl', 'telefono': '555555555',
        'direccion': 'Cond. El Sol 3', 'fecha_nacimiento': date(2007, 11, 25),
        'contacto_emergencia': 'Hermana: 777777777'
    }
]

for data in estudiantes_data:
    password = f"{data['nombre'][0]}{data['apellido_paterno']}".lower()
    auth_user = AuthUser.objects.create_user(
        rut=data['rut'],
        div=data['div'],
        password=password
    )
    usuario = Usuario.objects.create(
        nombre=data['nombre'],
        apellido_paterno=data['apellido_paterno'],
        apellido_materno=data['apellido_materno'],
        rut=data['rut'],
        div=data['div'],
        correo=data['correo'],
        telefono=data['telefono'],
        direccion=data['direccion'],
        fecha_nacimiento=data['fecha_nacimiento'],
        auth_user=auth_user
    )
    Estudiante.objects.create(usuario=usuario, contacto_emergencia=data['contacto_emergencia'])
    print(f"✅ Estudiante {usuario.nombre} {usuario.apellido_paterno} creado con contraseña '{password}'")
=======

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import AuthUser, Usuario, Administrativo
from django.contrib.auth.hashers import make_password

def create_admin_user():
    try:
        # Crear usuario de autenticación
        auth_user = AuthUser.objects.create(
            rut='admin',
            div='1',
            password=make_password('admin123'),
            is_admin=True
        )

        # Crear usuario
        usuario = Usuario.objects.create(
            nombre='Admin',
            apellido_paterno='Sistema',
            apellido_materno='GEM',
            rut='admin',
            div='1',
            correo='admin@gem.cl',
            telefono='123456789',
            direccion='Dirección Admin',
            fecha_nacimiento='2000-01-01',
            auth_user=auth_user
        )

        # Crear administrativo
        Administrativo.objects.create(
            usuario=usuario,
            rol='ADMINISTRADOR'
        )

        print('Usuario administrador creado exitosamente')
        print('Correo: admin@gem.cl')
        print('Contraseña: admin123')

    except Exception as e:
        print(f'Error al crear usuario: {str(e)}')

if __name__ == '__main__':
    create_admin_user() 
>>>>>>> Stashed changes
