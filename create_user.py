import os
import django
from datetime import time, date

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

# Importación de modelos
from Core.models import (
    AuthUser, Usuario, Administrativo, Docente, Estudiante,
    Especialidad, Curso, Asignatura, CursoAsignado, Clase, EstudianteAsignatura
)

# -----------------------------
# Crear especialidades
# -----------------------------
especialidades_nombres = [
    "Ninguna", "Matematicas", "Lenguaje", "Historia", "Biologia", "Fisica",
    "Quimica", "Ingles", "Educación Fisica", "Arte", "Tecnologia"
]

especialidades = []
for nombre in especialidades_nombres:
    esp, created = Especialidad.objects.get_or_create(nombre=nombre)
    especialidades.append(esp)

print("✅ Especialidades creadas")

# ------------------------------------
# Crear usuario administrador primero
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

# -----------------------------
# Crear cursos directamente
# -----------------------------
cursos_nombres = ['1A', '1B', '2A', '2B', '3A', '3B', '4A', '4B']

cursos = []
for nombre in cursos_nombres:
    curso, created = Curso.objects.get_or_create(letra=nombre)
    cursos.append(curso)

print("✅ Cursos creados")

# ------------------------------------
# Crear docentes (6 total)
# ------------------------------------
docentes_data = [
    # Los 2 ya existentes
    {
        'rut': '12345638', 'div': '9',
        'nombre': 'Juan', 'apellido_paterno': 'Pérez', 'apellido_materno': 'López',
        'correo': 'juan.perez@gem.cl', 'telefono': '111111111',
        'direccion': 'Calle Falsa 123', 'fecha_nacimiento': date(1980, 5, 10),
        'especialidad': especialidades[0]
    },
    {
        'rut': '23456786', 'div': '5',
        'nombre': 'María', 'apellido_paterno': 'González', 'apellido_materno': 'Ruiz',
        'correo': 'maria.gonzalez@gem.cl', 'telefono': '222222222',
        'direccion': 'Av. Siempre Viva 742', 'fecha_nacimiento': date(1985, 8, 20),
        'especialidad': especialidades[1]
    },
    # 4 nuevos
    {
        'rut': '87654321', 'div': '2',
        'nombre': 'Pedro', 'apellido_paterno': 'Sánchez', 'apellido_materno': 'Torres',
        'correo': 'pedro.sanchez@gem.cl', 'telefono': '333333333',
        'direccion': 'Calle Uno 111', 'fecha_nacimiento': date(1982, 6, 18),
        'especialidad': especialidades[2]
    },
    {
        'rut': '76543210', 'div': '4',
        'nombre': 'Lucía', 'apellido_paterno': 'Martínez', 'apellido_materno': 'Díaz',
        'correo': 'lucia.martinez@gem.cl', 'telefono': '444444444',
        'direccion': 'Calle Dos 222', 'fecha_nacimiento': date(1987, 9, 30),
        'especialidad': especialidades[3]
    },
    {
        'rut': '65432109', 'div': '6',
        'nombre': 'Javier', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Fuentes',
        'correo': 'javier.rojas@gem.cl', 'telefono': '555555555',
        'direccion': 'Calle Tres 333', 'fecha_nacimiento': date(1983, 2, 11),
        'especialidad': especialidades[4]
    },
    {
        'rut': '54321098', 'div': '8',
        'nombre': 'Carmen', 'apellido_paterno': 'Vidal', 'apellido_materno': 'Carrasco',
        'correo': 'carmen.vidal@gem.cl', 'telefono': '666666666',
        'direccion': 'Calle Cuatro 444', 'fecha_nacimiento': date(1984, 12, 3),
        'especialidad': especialidades[5]
    }
]

docentes = []
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
    docente = Docente.objects.create(usuario=usuario, especialidad=data['especialidad'])
    docentes.append(docente)
    print(f"✅ Docente {usuario.nombre} {usuario.apellido_paterno} creado con contraseña '{password}'")

# -----------------------------
# Crear asignaturas
# -----------------------------
asignaturas_info = [
    'Matemáticas', 'Lenguaje y Comunicación', 'Historia y Geografía',
    'Biología', 'Física', 'Química', 'Inglés', 'Educación Física',
    'Arte', 'Tecnología'
]

asignaturas = []
for nombre in asignaturas_info:
    asignatura, created = Asignatura.objects.get_or_create(nombre=nombre)
    asignaturas.append(asignatura)

print("✅ Asignaturas creadas")

# -----------------------------
# Asignar asignaturas a docentes (CursoAsignado)
# -----------------------------
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
hora_inicio = time(8, 0)
hora_fin = time(9, 30)

for curso in cursos:
    for i in range(3):  # 3 asignaturas por curso
        asignatura = asignaturas[(cursos.index(curso) + i) % len(asignaturas)]
        docente = docentes[(cursos.index(curso) + i) % len(docentes)]
        dia_asignado = dias[i % len(dias)]
        CursoAsignado.objects.get_or_create(
            asignatura=asignatura,
            docente=docente,
            dias=dia_asignado,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            sala=f"Sala {cursos.index(curso)+1}"
        )

print("✅ CursoAsignado creado con asignaturas y docentes")

# -----------------------------
# Crear clases para cada CursoAsignado
# -----------------------------
curso_asignados = CursoAsignado.objects.all()
for ca in curso_asignados:
    Clase.objects.get_or_create(
        curso=ca,
        fecha=date.today(),
        descripcion="Clase inicial",
        hora_inicio=ca.hora_inicio,
        hora_fin=ca.hora_fin
    )

print("✅ Clases creadas")

# ------------------------------------
# Crear estudiantes (30 total)
# ------------------------------------
# Nota: El listado completo debe estar definido aquí, te pongo un ejemplo con algunos
estudiantes_data= [
    {
        'rut': '34567890', 'div': 'K',
        'nombre': 'Luis', 'apellido_paterno': 'Ramírez', 'apellido_materno': 'Soto',
        'correo': 'luis.ramirez@gem.cl', 'telefono': '333333333',
        'direccion': 'Pje. Los Robles 45', 'fecha_nacimiento': date(2008, 3, 15),
        'contacto_emergencia': 'Mamá: 999999999'
    },
    {
        'rut': '12345678', 'div': '9',
        'nombre': 'Ana', 'apellido_paterno': 'González', 'apellido_materno': 'Mendoza',
        'correo': 'ana.gonzalez@gem.cl', 'telefono': '912345678',
        'direccion': 'Av. Libertad 123', 'fecha_nacimiento': date(2005, 7, 20),
        'contacto_emergencia': 'Papá: 998877665'
    },
    {
        'rut': '23456789', 'div': '1',
        'nombre': 'Carlos', 'apellido_paterno': 'Vargas', 'apellido_materno': 'Pérez',
        'correo': 'carlos.vargas@gem.cl', 'telefono': '923456789',
        'direccion': 'Calle Falsa 742', 'fecha_nacimiento': date(2007, 11, 5),
        'contacto_emergencia': 'Hermano: 987654321'
    },
    {
        'rut': '34567901', 'div': '2',
        'nombre': 'María', 'apellido_paterno': 'López', 'apellido_materno': 'Rojas',
        'correo': 'maria.lopez@gem.cl', 'telefono': '934567890',
        'direccion': 'Pasaje Luna 10', 'fecha_nacimiento': date(2006, 1, 10),
        'contacto_emergencia': 'Tía: 976543210'
    },
    {
        'rut': '45678902', 'div': '3',
        'nombre': 'Jorge', 'apellido_paterno': 'Torres', 'apellido_materno': 'Silva',
        'correo': 'jorge.torres@gem.cl', 'telefono': '945678901',
        'direccion': 'Av. Las Flores 55', 'fecha_nacimiento': date(2004, 5, 25),
        'contacto_emergencia': 'Mamá: 965432109'
    },
    {
        'rut': '56789012', 'div': '4',
        'nombre': 'Valentina', 'apellido_paterno': 'Rivas', 'apellido_materno': 'Navarro',
        'correo': 'valentina.rivas@gem.cl', 'telefono': '956789012',
        'direccion': 'Calle Sol 200', 'fecha_nacimiento': date(2008, 9, 30),
        'contacto_emergencia': 'Papá: 954321098'
    },
    {
        'rut': '67890123', 'div': '5',
        'nombre': 'Sebastián', 'apellido_paterno': 'Mendoza', 'apellido_materno': 'Campos',
        'correo': 'sebastian.mendoza@gem.cl', 'telefono': '967890123',
        'direccion': 'Av. Las Palmas 77', 'fecha_nacimiento': date(2005, 12, 1),
        'contacto_emergencia': 'Mamá: 943210987'
    },
    {
        'rut': '78901234', 'div': '6',
        'nombre': 'Camila', 'apellido_paterno': 'Fuentes', 'apellido_materno': 'Ortiz',
        'correo': 'camila.fuentes@gem.cl', 'telefono': '978901234',
        'direccion': 'Pje. La Reina 88', 'fecha_nacimiento': date(2007, 3, 14),
        'contacto_emergencia': 'Hermano: 932109876'
    },
    {
        'rut': '89012345', 'div': '7',
        'nombre': 'Diego', 'apellido_paterno': 'Sánchez', 'apellido_materno': 'Muñoz',
        'correo': 'diego.sanchez@gem.cl', 'telefono': '989012345',
        'direccion': 'Calle Norte 15', 'fecha_nacimiento': date(2006, 6, 22),
        'contacto_emergencia': 'Tía: 921098765'
    },
    {
        'rut': '90123456', 'div': '8',
        'nombre': 'Isidora', 'apellido_paterno': 'Vega', 'apellido_materno': 'Salazar',
        'correo': 'isidora.vega@gem.cl', 'telefono': '990123456',
        'direccion': 'Av. Sur 101', 'fecha_nacimiento': date(2004, 8, 18),
        'contacto_emergencia': 'Papá: 910987654'
    },
    {
        'rut': '11223344', 'div': 'K',
        'nombre': 'Felipe', 'apellido_paterno': 'Morales', 'apellido_materno': 'Guzmán',
        'correo': 'felipe.morales@gem.cl', 'telefono': '901234567',
        'direccion': 'Pje. Los Cedros 9', 'fecha_nacimiento': date(2005, 2, 28),
        'contacto_emergencia': 'Mamá: 909876543'
    },
    {
        'rut': '22334455', 'div': '1',
        'nombre': 'Martina', 'apellido_paterno': 'Herrera', 'apellido_materno': 'Paz',
        'correo': 'martina.herrera@gem.cl', 'telefono': '912345678',
        'direccion': 'Calle Nueva 456', 'fecha_nacimiento': date(2007, 4, 7),
        'contacto_emergencia': 'Hermano: 908765432'
    },
    {
        'rut': '33445566', 'div': '2',
        'nombre': 'Matías', 'apellido_paterno': 'Castillo', 'apellido_materno': 'Ríos',
        'correo': 'matias.castillo@gem.cl', 'telefono': '923456789',
        'direccion': 'Av. Central 321', 'fecha_nacimiento': date(2006, 10, 9),
        'contacto_emergencia': 'Tía: 907654321'
    },
    {
        'rut': '44556677', 'div': '3',
        'nombre': 'Lucía', 'apellido_paterno': 'Pérez', 'apellido_materno': 'Vargas',
        'correo': 'lucia.perez@gem.cl', 'telefono': '934567890',
        'direccion': 'Pje. Las Violetas 14', 'fecha_nacimiento': date(2008, 12, 19),
        'contacto_emergencia': 'Papá: 906543210'
    },
    {
        'rut': '55667788', 'div': '4',
        'nombre': 'Ignacio', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Díaz',
        'correo': 'ignacio.rojas@gem.cl', 'telefono': '945678901',
        'direccion': 'Calle Sur 33', 'fecha_nacimiento': date(2005, 1, 3),
        'contacto_emergencia': 'Mamá: 905432109'
    },
    {
        'rut': '66778899', 'div': '5',
        'nombre': 'Fernanda', 'apellido_paterno': 'Muñoz', 'apellido_materno': 'Cruz',
        'correo': 'fernanda.munoz@gem.cl', 'telefono': '956789012',
        'direccion': 'Av. Los Pinos 8', 'fecha_nacimiento': date(2007, 9, 26),
        'contacto_emergencia': 'Papá: 904321098'
    },
    {
        'rut': '77889900', 'div': '6',
        'nombre': 'Andrés', 'apellido_paterno': 'Salinas', 'apellido_materno': 'Lara',
        'correo': 'andres.salinas@gem.cl', 'telefono': '967890123',
        'direccion': 'Pje. Las Acacias 21', 'fecha_nacimiento': date(2006, 11, 12),
        'contacto_emergencia': 'Hermano: 903210987'
    },
    {
        'rut': '88990011', 'div': '7',
        'nombre': 'Sofía', 'apellido_paterno': 'Maldonado', 'apellido_materno': 'Torres',
        'correo': 'sofia.maldonado@gem.cl', 'telefono': '978901234',
        'direccion': 'Calle del Sol 77', 'fecha_nacimiento': date(2004, 7, 8),
        'contacto_emergencia': 'Tía: 902109876'
    },
    {
        'rut': '99001122', 'div': '8',
        'nombre': 'Tomás', 'apellido_paterno': 'Campos', 'apellido_materno': 'Fuentes',
        'correo': 'tomas.campos@gem.cl', 'telefono': '989012345',
        'direccion': 'Av. La Paz 4', 'fecha_nacimiento': date(2005, 5, 17),
        'contacto_emergencia': 'Mamá: 901098765'
    },
    {
        'rut': '10111213', 'div': 'K',
        'nombre': 'Antonia', 'apellido_paterno': 'Ortiz', 'apellido_materno': 'Vega',
        'correo': 'antonia.ortiz@gem.cl', 'telefono': '990123456',
        'direccion': 'Pje. Los Eucaliptos 23', 'fecha_nacimiento': date(2006, 8, 30),
        'contacto_emergencia': 'Papá: 900987654'
    },
    {
        'rut': '11121314', 'div': '1',
        'nombre': 'Gabriel', 'apellido_paterno': 'Salazar', 'apellido_materno': 'Morales',
        'correo': 'gabriel.salazar@gem.cl', 'telefono': '901234567',
        'direccion': 'Calle Luna 19', 'fecha_nacimiento': date(2007, 2, 11),
        'contacto_emergencia': 'Hermano: 899876543'
    },
    {
        'rut': '12131415', 'div': '2',
        'nombre': 'Isabel', 'apellido_paterno': 'Gutiérrez', 'apellido_materno': 'Herrera',
        'correo': 'isabel.gutierrez@gem.cl', 'telefono': '912345678',
        'direccion': 'Av. Los Olmos 50', 'fecha_nacimiento': date(2004, 3, 5),
        'contacto_emergencia': 'Tía: 898765432'
    },
    {
        'rut': '13141516', 'div': '3',
        'nombre': 'Nicolás', 'apellido_paterno': 'Rivas', 'apellido_materno': 'Castillo',
        'correo': 'nicolas.rivas@gem.cl', 'telefono': '923456789',
        'direccion': 'Pje. Los Nogales 12', 'fecha_nacimiento': date(2005, 10, 27),
        'contacto_emergencia': 'Papá: 897654321'
    },
    {
        'rut': '14151617', 'div': '4',
        'nombre': 'Emilia', 'apellido_paterno': 'Campos', 'apellido_materno': 'Pérez',
        'correo': 'emilia.campos@gem.cl', 'telefono': '934567890',
        'direccion': 'Calle Las Camelias 5', 'fecha_nacimiento': date(2006, 12, 16),
        'contacto_emergencia': 'Mamá: 896543210'
    },
    {
        'rut': '15161718', 'div': '5',
        'nombre': 'Juan', 'apellido_paterno': 'Lara', 'apellido_materno': 'Salinas',
        'correo': 'juan.lara@gem.cl', 'telefono': '945678901',
        'direccion': 'Av. Los Alamos 101', 'fecha_nacimiento': date(2007, 1, 22),
        'contacto_emergencia': 'Papá: 895432109'
    },
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
    Estudiante.objects.create(
        usuario=usuario,
        contacto_emergencia=data['contacto_emergencia']
    )
    print(f"✅ Estudiante {usuario.nombre} {usuario.apellido_paterno} creado con contraseña '{password}'")

print("✅ Estudiantes creados")
