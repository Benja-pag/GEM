import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from Core.models import (
    AuthUser, Usuario, Especialidad, Docente, Administrativo, Curso, Estudiante, EvaluacionBase, Asignatura, AsignaturaImpartida, AsignaturaInscrita
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

# Crear especialidades
especialidades_nombres = [
    "Matemáticas", "Lenguaje", "Historia", "Biología", "Física"
]
especialidades = []
for nombre in especialidades_nombres:
    esp, _ = Especialidad.objects.get_or_create(nombre=nombre)
    especialidades.append(esp)

# Crear docentes
docentes_data = [
    {'rut': '12345678', 'div': '1', 'nombre': 'Juan', 'apellido_paterno': 'Perez', 'apellido_materno': 'Lopez', 'correo': 'juan.perez@gem.cl', 'telefono': '111111111', 'direccion': 'Calle Falsa 123', 'fecha_nacimiento': date(1980, 5, 10), 'especialidad': especialidades[0], 'password': 'JPerez'},
    {'rut': '23456789', 'div': '2', 'nombre': 'Maria', 'apellido_paterno': 'Gonzalez', 'apellido_materno': 'Ruiz', 'correo': 'maria.gonzalez@gem.cl', 'telefono': '222222222', 'direccion': 'Av. Siempre Viva 742', 'fecha_nacimiento': date(1985, 8, 20), 'especialidad': especialidades[1], 'password': 'MGonzalez'},
    {'rut': '34567890', 'div': '3', 'nombre': 'Paula', 'apellido_paterno': 'Muñoz', 'apellido_materno': 'Salinas', 'correo': 'paula.munoz@gem.cl', 'telefono': '333333333', 'direccion': 'Calle Nueva 456', 'fecha_nacimiento': date(1979, 3, 12), 'especialidad': especialidades[2], 'password': 'PMunoz'},
    {'rut': '45678901', 'div': '4', 'nombre': 'Ricardo', 'apellido_paterno': 'Soto', 'apellido_materno': 'Paredes', 'correo': 'ricardo.soto@gem.cl', 'telefono': '444444444', 'direccion': 'Av. Central 789', 'fecha_nacimiento': date(1975, 11, 23), 'especialidad': especialidades[3], 'password': 'RSoto'},
    {'rut': '56789012', 'div': '5', 'nombre': 'Claudia', 'apellido_paterno': 'Fernandez', 'apellido_materno': 'Cordero', 'correo': 'claudia.fernandez@gem.cl', 'telefono': '555555555', 'direccion': 'Calle Principal 123', 'fecha_nacimiento': date(1982, 7, 5), 'especialidad': especialidades[4], 'password': 'CFernandez'},
]
docentes = []
for data in docentes_data:
    auth_user, _ = AuthUser.objects.get_or_create(
        rut=data['rut'],
        defaults={'div': data['div'], 'password': make_password(data['password'])}
    )
    usuario, _ = Usuario.objects.get_or_create(
        rut=data['rut'],
        defaults={
            'nombre': data['nombre'],
            'apellido_paterno': data['apellido_paterno'],
            'apellido_materno': data['apellido_materno'],
            'div': data['div'],
            'correo': data['correo'],
            'telefono': data['telefono'],
            'direccion': data['direccion'],
            'fecha_nacimiento': data['fecha_nacimiento'],
            'auth_user': auth_user
        }
    )
    docente, _ = Docente.objects.get_or_create(
        usuario=usuario,
        defaults={'especialidad': data['especialidad']}
    )
    docentes.append(docente)

# Crear cursos
cursos_data = [
    {'nivel': 1, 'letra': 'A'},
    {'nivel': 1, 'letra': 'B'},
    {'nivel': 2, 'letra': 'A'},
    {'nivel': 2, 'letra': 'B'},
]
cursos = []
for data in cursos_data:
    curso, _ = Curso.objects.get_or_create(nivel=data['nivel'], letra=data['letra'])
    cursos.append(curso)

# Crear asignaturas
asignaturas_nombres = [
    "Matemáticas", "Lenguaje", "Historia", "Biología", "Física", "Química", "Inglés", "Educación Física", "Arte", "Música"
]
asignaturas = []

for i in range(1, 5):
    for nombre in asignaturas_nombres:
        asignatura, _ = Asignatura.objects.get_or_create(nombre=nombre, nivel=i)
        asignaturas.append(asignatura)

# Crear evaluaciones base para cada asignatura
for asignatura in asignaturas:
    EvaluacionBase.objects.get_or_create(
        asignatura=asignatura,
        nombre="Prueba 1",
        defaults={'ponderacion': 30.0, 'descripcion': 'Primera prueba parcial'}
    )
    EvaluacionBase.objects.get_or_create(
        asignatura=asignatura,
        nombre="Prueba 2",
        defaults={'ponderacion': 30.0, 'descripcion': 'Segunda prueba parcial'}
    )
    EvaluacionBase.objects.get_or_create(
        asignatura=asignatura,
        nombre="Examen Final",
        defaults={'ponderacion': 40.0, 'descripcion': 'Examen final del curso'}
    )

# Crear asignaturas impartidas (ramo)
asignaturas_impartidas = []

for curso in cursos:
    for asignatura in Asignatura.objects.filter(nivel=curso.nivel):
        docente = Docente.objects.order_by('?').first()  # Elige un docente al azar o según lógica
        codigo = f"{asignatura.nombre[:3].upper()}_{curso.nivel}{curso.letra}"
        ai, _ = AsignaturaImpartida.objects.get_or_create(
            asignatura=asignatura,
            docente=docente,
            defaults={
                'codigo': codigo,
                'horario': f"Lunes {8 + i}:00-09:30"
        }
        )
        asignaturas_impartidas.append(ai)

# Crear estudiantes 
estudiantes_data = [
    {'rut': '11111111', 'div': '1', 'nombre': 'Ana', 'apellido_paterno': 'Gomez', 'apellido_materno': 'Perez', 'correo': 'ana.gomez@gem.cl', 'telefono': '912345678', 'direccion': 'Calle Uno 1', 'fecha_nacimiento': date(2008, 3, 15), 'contacto_emergencia': 'Mama: 999999999', 'curso': cursos[0], 'password': 'anagomez'},
    {'rut': '22222222', 'div': '2', 'nombre': 'Luis', 'apellido_paterno': 'Ramirez', 'apellido_materno': 'Soto', 'correo': 'luis.ramirez@gem.cl', 'telefono': '923456789', 'direccion': 'Calle Dos 2', 'fecha_nacimiento': date(2008, 5, 20), 'contacto_emergencia': 'Papa: 888888888', 'curso': cursos[1], 'password': 'luisramirez'},
    {'rut': '33333333', 'div': '3', 'nombre': 'Camila', 'apellido_paterno': 'Fuentes', 'apellido_materno': 'Riquelme', 'correo': 'camila.fuentes@gem.cl', 'telefono': '934567890', 'direccion': 'Calle Azul 45', 'fecha_nacimiento': date(2006, 1, 19), 'contacto_emergencia': 'Mama: 843210987', 'curso': cursos[0], 'password': 'cfuentes'},
    {'rut': '44444444', 'div': '4', 'nombre': 'Benjamin', 'apellido_paterno': 'Vera', 'apellido_materno': 'Hidalgo', 'correo': 'benjamin.vera@gem.cl', 'telefono': '945678901', 'direccion': 'Villa Esperanza 9', 'fecha_nacimiento': date(2007, 8, 30), 'contacto_emergencia': 'Abuela: 854321098', 'curso': cursos[2], 'password': 'bvera'},
    {'rut': '55555555', 'div': '5', 'nombre': 'Martina', 'apellido_paterno': 'Silva', 'apellido_materno': 'Venegas', 'correo': 'martina.silva@gem.cl', 'telefono': '956789012', 'direccion': 'Av. Lomas 72', 'fecha_nacimiento': date(2005, 5, 3), 'contacto_emergencia': 'Tia: 865432109', 'curso': cursos[2], 'password': 'msilva'},
    {'rut': '66666666', 'div': '6', 'nombre': 'Isidora', 'apellido_paterno': 'Vega', 'apellido_materno': 'Salazar', 'correo': 'isidora.vega@gem.cl', 'telefono': '990123456', 'direccion': 'Av. Sur 101', 'fecha_nacimiento': date(2004, 8, 18), 'contacto_emergencia': 'Papa: 910987654', 'curso': cursos[3], 'password': 'ivega'},
    {'rut': '77777777', 'div': '7', 'nombre': 'Jorge', 'apellido_paterno': 'Torres', 'apellido_materno': 'Silva', 'correo': 'jorge.torres@gem.cl', 'telefono': '945678901', 'direccion': 'Av. Las Flores 55', 'fecha_nacimiento': date(2004, 5, 25), 'contacto_emergencia': 'Mama: 965432109', 'curso': cursos[3], 'password': 'jtorres'},
    {'rut': '88888888', 'div': '8', 'nombre': 'Valentina', 'apellido_paterno': 'Rivas', 'apellido_materno': 'Navarro', 'correo': 'valentina.rivas@gem.cl', 'telefono': '956789012', 'direccion': 'Calle Sol 200', 'fecha_nacimiento': date(2008, 9, 30), 'contacto_emergencia': 'Papa: 954321098', 'curso': cursos[1], 'password': 'vrivas'},
    {'rut': '99999999', 'div': '9', 'nombre': 'Sebastian', 'apellido_paterno': 'Mendoza', 'apellido_materno': 'Campos', 'correo': 'sebastian.mendoza@gem.cl', 'telefono': '967890123', 'direccion': 'Av. Las Palmas 77', 'fecha_nacimiento': date(2005, 12, 1), 'contacto_emergencia': 'Mama: 943210987', 'curso': cursos[0], 'password': 'smendoza'},
    {'rut': '10101010', 'div': 'K', 'nombre': 'Felipe', 'apellido_paterno': 'Morales', 'apellido_materno': 'Guzman', 'correo': 'felipe.morales@gem.cl', 'telefono': '901234567', 'direccion': 'Pje. Los Cedros 9', 'fecha_nacimiento': date(2005, 2, 28), 'contacto_emergencia': 'Mama: 909876543', 'curso': cursos[1], 'password': 'fmorales'},
]

for data in estudiantes_data:
    auth_user, _ = AuthUser.objects.get_or_create(
        rut=data['rut'],
        defaults={'div': data['div'], 'password': make_password(data['password'])}
    )
    usuario, _ = Usuario.objects.get_or_create(
        rut=data['rut'],
        defaults={
            'nombre': data['nombre'],
            'apellido_paterno': data['apellido_paterno'],
            'apellido_materno': data['apellido_materno'],
            'div': data['div'],
            'correo': data['correo'],
            'telefono': data['telefono'],
            'direccion': data['direccion'],
            'fecha_nacimiento': data['fecha_nacimiento'],
            'auth_user': auth_user
        }
    )
    Estudiante.objects.get_or_create(
        usuario=usuario,
        defaults={
            'contacto_emergencia': data['contacto_emergencia'],
            'curso': data['curso']
        }
    )

# Asignar asignaturas impartidas a estudiantes

for estudiante in Estudiante.objects.all():
    asignaturas_impartidas = AsignaturaImpartida.objects.filter(asignatura__nivel=estudiante.curso.nivel)
    for asignatura_impartida in asignaturas_impartidas:
        AsignaturaInscrita.objects.get_or_create(
            estudiante=estudiante,
            asignatura_impartida=asignatura_impartida
        )

print("✅ Docentes, cursos, asignaturas, asignaturas impartidas y estudiantes creados con éxito.")