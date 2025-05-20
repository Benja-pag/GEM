import os
import django
from datetime import time, date
from django.contrib.auth.hashers import make_password

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

# Importación de modelos
from Core.models import (
    AuthUser, Usuario, Administrativo, Docente, Estudiante,
    Especialidad, Clase, Asignatura, ClaseAsignatura, Electivo,
    InscripcionElectivo, CalendarioClase, CalendarioColegio
)

# -----------------------------
# Crear especialidades
# -----------------------------
especialidades_nombres = [
    "Ninguna", "Matematicas", "Lenguaje", "Historia", "Biologia", "Fisica",
    "Quimica", "Ingles", "Educación Fisica", "Arte", "Tecnologia",

    # Electivos para una Escuela Humanista
    "Filosofía y Ética",
    "Literatura y Escritura Creativa",
    "Historia del Arte y Cultura",
    "Psicología y Desarrollo Humano",
    "Sociología y Estudios Sociales",
    "Teatro y Expresión Corporal",
    "Música y Composición",
    "Taller de Debate y Oratoria",
    "Educación Ambiental y Sostenibilidad",
    "Derechos Humanos y Ciudadanía",

    # Electivos para una Escuela Científica
    "Biología Avanzada",
    "Química Experimental",
    "Física Aplicada",
    "Matemáticas Discretas",
    "Programación y Robótica",
    "Astronomía y Ciencias del Espacio",
    "Investigación Científica y Método Experimental",
    "Tecnología e Innovación",
    "Ciencias de la Tierra y Medio Ambiente",
    "Estadística y Análisis de Datos"
]

especialidades = []
for nombre in especialidades_nombres:
    esp, created = Especialidad.objects.get_or_create(nombre=nombre)
    especialidades.append(esp)

print("✅ Especialidades creadas")

# ------------------------------------
# Crear usuario administrador primero
# ------------------------------------
try:
    admin_auth_user = AuthUser.objects.get(rut='20120767')
    print('✅ Usuario administrador ya existe')
except AuthUser.DoesNotExist:
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
# Crear docentes (6 total)
# ------------------------------------
docentes_data = [
    {
        'rut': '12345638', 'div': '9',
        'nombre': 'Juan', 'apellido_paterno': 'Pérez', 'apellido_materno': 'López',
        'correo': 'juan.perez@gem.cl', 'telefono': '111111111',
        'direccion': 'Calle Falsa 123', 'fecha_nacimiento': date(1980, 5, 10),
        'especialidad': especialidades[0]  # Ninguna
    },
    {
        'rut': '23456786', 'div': '5',
        'nombre': 'María', 'apellido_paterno': 'González', 'apellido_materno': 'Ruiz',
        'correo': 'maria.gonzalez@gem.cl', 'telefono': '222222222',
        'direccion': 'Av. Siempre Viva 742', 'fecha_nacimiento': date(1985, 8, 20),
        'especialidad': especialidades[1]  # Matemáticas
    },
    {
        'rut': '87654321', 'div': '2',
        'nombre': 'Pedro', 'apellido_paterno': 'Sánchez', 'apellido_materno': 'Torres',
        'correo': 'pedro.sanchez@gem.cl', 'telefono': '333333333',
        'direccion': 'Calle Uno 111', 'fecha_nacimiento': date(1982, 6, 18),
        'especialidad': especialidades[2]  # Lenguaje
    },
    {
        'rut': '76543210', 'div': '4',
        'nombre': 'Lucía', 'apellido_paterno': 'Martínez', 'apellido_materno': 'Díaz',
        'correo': 'lucia.martinez@gem.cl', 'telefono': '444444444',
        'direccion': 'Calle Dos 222', 'fecha_nacimiento': date(1987, 9, 30),
        'especialidad': especialidades[3]  # Historia
    },
    {
        'rut': '65432109', 'div': '6',
        'nombre': 'Javier', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Fuentes',
        'correo': 'javier.rojas@gem.cl', 'telefono': '555555555',
        'direccion': 'Calle Tres 333', 'fecha_nacimiento': date(1983, 2, 11),
        'especialidad': especialidades[4]  # Biología
    },
    {
        'rut': '54321098', 'div': '8',
        'nombre': 'Carmen', 'apellido_paterno': 'Vidal', 'apellido_materno': 'Carrasco',
        'correo': 'carmen.vidal@gem.cl', 'telefono': '666666666',
        'direccion': 'Calle Cuatro 444', 'fecha_nacimiento': date(1984, 12, 3),
        'especialidad': especialidades[5]  # Física
    },
    {
        'rut': '19876543', 'div': '1',
        'nombre': 'Isabel', 'apellido_paterno': 'Fernández', 'apellido_materno': 'Salazar',
        'correo': 'isabel.fernandez@gem.cl', 'telefono': '121212121',
        'direccion': 'Calle Nueve 999', 'fecha_nacimiento': date(1988, 6, 12),
        'especialidad': especialidades[10]  # Tecnología
    },
    {
        'rut': '29876543', 'div': '2',
        'nombre': 'Tomás', 'apellido_paterno': 'Herrera', 'apellido_materno': 'Bravo',
        'correo': 'tomas.herrera@gem.cl', 'telefono': '131313131',
        'direccion': 'Calle Diez 1010', 'fecha_nacimiento': date(1981, 1, 8),
        'especialidad': especialidades[0]  # Ninguna
    },
    {
        'rut': '39876543', 'div': '3',
        'nombre': 'Daniela', 'apellido_paterno': 'Reyes', 'apellido_materno': 'Muñoz',
        'correo': 'daniela.reyes@gem.cl', 'telefono': '141414141',
        'direccion': 'Calle Once 1111', 'fecha_nacimiento': date(1990, 10, 14),
        'especialidad': especialidades[2]  # Lenguaje
    },
    {
        'rut': '49876543', 'div': '4',
        'nombre': 'Matías', 'apellido_paterno': 'Lagos', 'apellido_materno': 'Zamora',
        'correo': 'matias.lagos@gem.cl', 'telefono': '151515151',
        'direccion': 'Calle Doce 1212', 'fecha_nacimiento': date(1985, 5, 5),
        'especialidad': especialidades[3]  # Historia
    },
    {
        'rut': '59876543', 'div': '5',
        'nombre': 'Fernanda', 'apellido_paterno': 'Castro', 'apellido_materno': 'Ahumada',
        'correo': 'fernanda.castro@gem.cl', 'telefono': '161616161',
        'direccion': 'Calle Trece 1313', 'fecha_nacimiento': date(1986, 8, 19),
        'especialidad': especialidades[4]  # Biología
    },
    {
        'rut': '69876543', 'div': '6',
        'nombre': 'Sebastián', 'apellido_paterno': 'Gutiérrez', 'apellido_materno': 'Ovalle',
        'correo': 'sebastian.gutierrez@gem.cl', 'telefono': '171717171',
        'direccion': 'Calle Catorce 1414', 'fecha_nacimiento': date(1983, 2, 2),
        'especialidad': especialidades[5]  # Física
    },
    {
        'rut': '79876543', 'div': '7',
        'nombre': 'Rocío', 'apellido_paterno': 'Alvarado', 'apellido_materno': 'Contreras',
        'correo': 'rocio.alvarado@gem.cl', 'telefono': '181818181',
        'direccion': 'Calle Quince 1515', 'fecha_nacimiento': date(1987, 7, 7),
        'especialidad': especialidades[6]  # Química
    },
    {
        'rut': '88888888', 'div': '8',
        'nombre': 'Cristóbal', 'apellido_paterno': 'Navarro', 'apellido_materno': 'Morales',
        'correo': 'cristobal.navarro@gem.cl', 'telefono': '191919191',
        'direccion': 'Calle Dieciséis 1616', 'fecha_nacimiento': date(1980, 4, 22),
        'especialidad': especialidades[7]  # Inglés
    },
    {
        'rut': '99999999', 'div': '9',
        'nombre': 'Valentina', 'apellido_paterno': 'Saavedra', 'apellido_materno': 'León',
        'correo': 'valentina.saavedra@gem.cl', 'telefono': '202020202',
        'direccion': 'Calle Diecisiete 1717', 'fecha_nacimiento': date(1991, 3, 17),
        'especialidad': especialidades[8]  # Educación Física
    },
    {
        'rut': '11111111', 'div': '1',
        'nombre': 'Felipe', 'apellido_paterno': 'Ortega', 'apellido_materno': 'Riquelme',
        'correo': 'felipe.ortega@gem.cl', 'telefono': '212121212',
        'direccion': 'Calle Dieciocho 1818', 'fecha_nacimiento': date(1989, 11, 11),
        'especialidad': especialidades[9]  # Arte
    },
    {
        'rut': '12121212', 'div': '2',
        'nombre': 'Antonia', 'apellido_paterno': 'Silva', 'apellido_materno': 'Paredes',
        'correo': 'antonia.silva@gem.cl', 'telefono': '222222222',
        'direccion': 'Calle Diecinueve 1919', 'fecha_nacimiento': date(1982, 12, 24),
        'especialidad': especialidades[10]  # Tecnología
    }
]

docentes = []
for data in docentes_data:
    password = f"{data['nombre'][0]}{data['apellido_paterno']}".lower()
    
    # Crear o obtener el usuario de autenticación
    auth_user, created = AuthUser.objects.get_or_create(
        rut=data['rut'],
        defaults={
            'div': data['div'],
            'password': make_password(password)  # Hashear la contraseña
        }
    )
    
    if not created:
        # Si el usuario ya existe, actualizar la contraseña
        auth_user.set_password(password)
        auth_user.save()
    
    # Crear o obtener el usuario
    usuario, created = Usuario.objects.get_or_create(
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
    
    # Crear o obtener el docente
    docente, created = Docente.objects.get_or_create(
        usuario=usuario,
        defaults={
            'especialidad': data['especialidad']
        }
    )
    
    docentes.append(docente)
    if created:
        print(f"✅ Docente {usuario.nombre} {usuario.apellido_paterno} creado con contraseña '{password}'")
    else:
        print(f"✅ Docente {usuario.nombre} {usuario.apellido_paterno} ya existe")

# -----------------------------
# Crear cursos directamente
# -----------------------------
cursos_nombres = ['1A', '1B', '1C', '1D', '2A', '2B', '2C', '2D', '3A', '3B', '3C', '3D', '4A', '4B', '4C', '4D']

cursos = []
for i, nombre in enumerate(cursos_nombres):
    # Asignar un profesor jefe a cada curso de manera cíclica
    profesor_jefe = docentes[i % len(docentes)]
    curso, created = Clase.objects.get_or_create(
        nombre=nombre,
        defaults={
            'profesor_jefe': profesor_jefe,
            'sala': f"Sala {nombre}"  # Asignar una sala por defecto
        }
    )
    cursos.append(curso)
    print(f"✅ Curso {nombre} creado con profesor jefe {profesor_jefe.usuario.nombre} {profesor_jefe.usuario.apellido_paterno}")

print("✅ Cursos creados")

# -----------------------------
# Crear asignaturas
# -----------------------------
asignaturas_info = [
    {
        'nombre': 'Matemáticas',
        'codigo': 'MAT001',
        'dia': 'Lunes',
        'horario': time(8, 0),
        'docente': docentes[1],  # María González - Matemáticas
        'clase': cursos[0]  # 1A
    },
    {
        'nombre': 'Lenguaje y Comunicación',
        'codigo': 'LEN001',
        'dia': 'Martes',
        'horario': time(8, 0),
        'docente': docentes[2],  # Pedro Sánchez - Lenguaje
        'clase': cursos[0]  # 1A
    },
    {
        'nombre': 'Historia y Geografía',
        'codigo': 'HIS001',
        'dia': 'Miércoles',
        'horario': time(8, 0),
        'docente': docentes[3],  # Lucía Martínez - Historia
        'clase': cursos[0]  # 1A
    },
    {
        'nombre': 'Biología',
        'codigo': 'BIO001',
        'dia': 'Jueves',
        'horario': time(8, 0),
        'docente': docentes[4],  # Javier Rojas - Biología
        'clase': cursos[0]  # 1A
    },
    {
        'nombre': 'Física',
        'codigo': 'FIS001',
        'dia': 'Viernes',
        'horario': time(8, 0),
        'docente': docentes[5],  # Carmen Vidal - Física
        'clase': cursos[0]  # 1A
    }
]

asignaturas = []  # Lista para almacenar las asignaturas creadas
for info in asignaturas_info:
    asignatura, created = Asignatura.objects.get_or_create(
        codigo=info['codigo'],
        clase=info['clase'],
        defaults={
            'nombre': info['nombre'],
            'docente': info['docente'],
            'dia': info['dia'],
            'horario': info['horario']
        }
    )
    asignaturas.append(asignatura)  # Agregar la asignatura a la lista
    if created:
        print(f"✅ Asignatura {info['nombre']} creada para {info['clase'].nombre} con profesor {info['docente'].usuario.nombre} {info['docente'].usuario.apellido_paterno}")

print("✅ Asignaturas creadas")

# -----------------------------
# Asignar asignaturas a docentes (ClaseAsignatura)
# -----------------------------
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
hora_inicio = time(8, 0)
hora_fin = time(9, 30)

for curso in cursos:
    for i in range(3):  # 3 asignaturas por curso
        asignatura = asignaturas[(cursos.index(curso) + i) % len(asignaturas)]
        docente = docentes[(cursos.index(curso) + i) % len(docentes)]
        dia_asignado = dias[i % len(dias)]
        ClaseAsignatura.objects.get_or_create(
            docente=docente,
            asignatura=asignatura,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            dia=dia_asignado,
            curso=curso.nombre
        )

print("✅ ClaseAsignatura creado con asignaturas y docentes")

# -----------------------------
# Crear estudiantes
# -----------------------------
estudiantes_data = [
    {
        'rut': '34567890', 'div': 'K',
        'nombre': 'Luis', 'apellido_paterno': 'Ramírez', 'apellido_materno': 'Soto',
        'correo': 'luis.ramirez@gem.cl', 'telefono': '333333333',
        'direccion': 'Pje. Los Robles 45', 'fecha_nacimiento': date(2008, 3, 15),
        'contacto_emergencia': 'Mamá: 999999999',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '12345678', 'div': '9',
        'nombre': 'Ana', 'apellido_paterno': 'González', 'apellido_materno': 'Mendoza',
        'correo': 'ana.gonzalez@gem.cl', 'telefono': '912345678',
        'direccion': 'Av. Libertad 123', 'fecha_nacimiento': date(2005, 7, 20),
        'contacto_emergencia': 'Papá: 998877665',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '23456789', 'div': '1',
        'nombre': 'Carlos', 'apellido_paterno': 'Vargas', 'apellido_materno': 'Pérez',
        'correo': 'carlos.vargas@gem.cl', 'telefono': '923456789',
        'direccion': 'Calle Falsa 742', 'fecha_nacimiento': date(2007, 11, 5),
        'contacto_emergencia': 'Hermano: 987654321',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '34567901', 'div': '2',
        'nombre': 'María', 'apellido_paterno': 'López', 'apellido_materno': 'Rojas',
        'correo': 'maria.lopez@gem.cl', 'telefono': '934567890',
        'direccion': 'Pasaje Luna 10', 'fecha_nacimiento': date(2006, 1, 10),
        'contacto_emergencia': 'Tía: 976543210',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '45678902', 'div': '3',
        'nombre': 'Jorge', 'apellido_paterno': 'Torres', 'apellido_materno': 'Silva',
        'correo': 'jorge.torres@gem.cl', 'telefono': '945678901',
        'direccion': 'Av. Las Flores 55', 'fecha_nacimiento': date(2004, 5, 25),
        'contacto_emergencia': 'Mamá: 965432109',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '56789012', 'div': '4',
        'nombre': 'Valentina', 'apellido_paterno': 'Rivas', 'apellido_materno': 'Navarro',
        'correo': 'valentina.rivas@gem.cl', 'telefono': '956789012',
        'direccion': 'Calle Sol 200', 'fecha_nacimiento': date(2008, 9, 30),
        'contacto_emergencia': 'Papá: 954321098',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '67890123', 'div': '5',
        'nombre': 'Sebastián', 'apellido_paterno': 'Mendoza', 'apellido_materno': 'Campos',
        'correo': 'sebastian.mendoza@gem.cl', 'telefono': '967890123',
        'direccion': 'Av. Las Palmas 77', 'fecha_nacimiento': date(2005, 12, 1),
        'contacto_emergencia': 'Mamá: 943210987',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '78901234', 'div': '6',
        'nombre': 'Camila', 'apellido_paterno': 'Fuentes', 'apellido_materno': 'Ortiz',
        'correo': 'camila.fuentes@gem.cl', 'telefono': '978901234',
        'direccion': 'Pje. La Reina 88', 'fecha_nacimiento': date(2007, 3, 14),
        'contacto_emergencia': 'Hermano: 932109876',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '89012345', 'div': '7',
        'nombre': 'Diego', 'apellido_paterno': 'Sánchez', 'apellido_materno': 'Muñoz',
        'correo': 'diego.sanchez@gem.cl', 'telefono': '989012345',
        'direccion': 'Calle Norte 15', 'fecha_nacimiento': date(2006, 6, 22),
        'contacto_emergencia': 'Tía: 921098765',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '90123456', 'div': '8',
        'nombre': 'Isidora', 'apellido_paterno': 'Vega', 'apellido_materno': 'Salazar',
        'correo': 'isidora.vega@gem.cl', 'telefono': '990123456',
        'direccion': 'Av. Sur 101', 'fecha_nacimiento': date(2004, 8, 18),
        'contacto_emergencia': 'Papá: 910987654',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '11223344', 'div': 'K',
        'nombre': 'Felipe', 'apellido_paterno': 'Morales', 'apellido_materno': 'Guzmán',
        'correo': 'felipe.morales@gem.cl', 'telefono': '901234567',
        'direccion': 'Pje. Los Cedros 9', 'fecha_nacimiento': date(2005, 2, 28),
        'contacto_emergencia': 'Mamá: 909876543',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '22334455', 'div': '1',
        'nombre': 'Martina', 'apellido_paterno': 'Herrera', 'apellido_materno': 'Paz',
        'correo': 'martina.herrera@gem.cl', 'telefono': '912345678',
        'direccion': 'Calle Nueva 456', 'fecha_nacimiento': date(2007, 4, 7),
        'contacto_emergencia': 'Hermano: 908765432',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '33445566', 'div': '2',
        'nombre': 'Matías', 'apellido_paterno': 'Castillo', 'apellido_materno': 'Ríos',
        'correo': 'matias.castillo@gem.cl', 'telefono': '923456789',
        'direccion': 'Av. Central 321', 'fecha_nacimiento': date(2006, 10, 9),
        'contacto_emergencia': 'Tía: 907654321',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '44556677', 'div': '3',
        'nombre': 'Lucía', 'apellido_paterno': 'Pérez', 'apellido_materno': 'Vargas',
        'correo': 'lucia.perez@gem.cl', 'telefono': '934567890',
        'direccion': 'Pje. Las Violetas 14', 'fecha_nacimiento': date(2008, 12, 19),
        'contacto_emergencia': 'Papá: 906543210',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '55667788', 'div': '4',
        'nombre': 'Ignacio', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Díaz',
        'correo': 'ignacio.rojas@gem.cl', 'telefono': '945678901',
        'direccion': 'Calle Sur 33', 'fecha_nacimiento': date(2005, 1, 3),
        'contacto_emergencia': 'Mamá: 905432109',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '66778899', 'div': '5',
        'nombre': 'Fernanda', 'apellido_paterno': 'Muñoz', 'apellido_materno': 'Cruz',
        'correo': 'fernanda.munoz@gem.cl', 'telefono': '956789012',
        'direccion': 'Av. Los Pinos 8', 'fecha_nacimiento': date(2007, 9, 26),
        'contacto_emergencia': 'Papá: 904321098',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '77889900', 'div': '6',
        'nombre': 'Andrés', 'apellido_paterno': 'Salinas', 'apellido_materno': 'Lara',
        'correo': 'andres.salinas@gem.cl', 'telefono': '967890123',
        'direccion': 'Pje. Las Acacias 21', 'fecha_nacimiento': date(2006, 11, 12),
        'contacto_emergencia': 'Hermano: 903210987',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '88990011', 'div': '7',
        'nombre': 'Sofía', 'apellido_paterno': 'Maldonado', 'apellido_materno': 'Torres',
        'correo': 'sofia.maldonado@gem.cl', 'telefono': '978901234',
        'direccion': 'Calle del Sol 77', 'fecha_nacimiento': date(2004, 7, 8),
        'contacto_emergencia': 'Tía: 902109876',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '99001122', 'div': '8',
        'nombre': 'Tomás', 'apellido_paterno': 'Campos', 'apellido_materno': 'Fuentes',
        'correo': 'tomas.campos@gem.cl', 'telefono': '989012345',
        'direccion': 'Av. La Paz 4', 'fecha_nacimiento': date(2005, 5, 17),
        'contacto_emergencia': 'Mamá: 901098765',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '10111213', 'div': 'K',
        'nombre': 'Antonia', 'apellido_paterno': 'Ortiz', 'apellido_materno': 'Vega',
        'correo': 'antonia.ortiz@gem.cl', 'telefono': '990123456',
        'direccion': 'Pje. Los Eucaliptos 23', 'fecha_nacimiento': date(2006, 8, 30),
        'contacto_emergencia': 'Papá: 900987654',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '11121314', 'div': '1',
        'nombre': 'Gabriel', 'apellido_paterno': 'Salazar', 'apellido_materno': 'Morales',
        'correo': 'gabriel.salazar@gem.cl', 'telefono': '901234567',
        'direccion': 'Calle Luna 19', 'fecha_nacimiento': date(2007, 2, 11),
        'contacto_emergencia': 'Hermano: 899876543',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '12131415', 'div': '2',
        'nombre': 'Isabel', 'apellido_paterno': 'Gutiérrez', 'apellido_materno': 'Herrera',
        'correo': 'isabel.gutierrez@gem.cl', 'telefono': '912345678',
        'direccion': 'Av. Los Olmos 50', 'fecha_nacimiento': date(2004, 3, 5),
        'contacto_emergencia': 'Tía: 898765432',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '13141516', 'div': '3',
        'nombre': 'Nicolás', 'apellido_paterno': 'Rivas', 'apellido_materno': 'Castillo',
        'correo': 'nicolas.rivas@gem.cl', 'telefono': '923456789',
        'direccion': 'Pje. Los Nogales 12', 'fecha_nacimiento': date(2005, 10, 27),
        'contacto_emergencia': 'Papá: 897654321',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '14151617', 'div': '4',
        'nombre': 'Emilia', 'apellido_paterno': 'Campos', 'apellido_materno': 'Pérez',
        'correo': 'emilia.campos@gem.cl', 'telefono': '934567890',
        'direccion': 'Calle Las Camelias 5', 'fecha_nacimiento': date(2006, 12, 16),
        'contacto_emergencia': 'Mamá: 896543210',
        'clase': cursos[0]  # Asignamos a la primera clase
    },
    {
        'rut': '15161718', 'div': '5',
        'nombre': 'Juan', 'apellido_paterno': 'Lara', 'apellido_materno': 'Salinas',
        'correo': 'juan.lara@gem.cl', 'telefono': '945678901',
        'direccion': 'Av. Los Alamos 101', 'fecha_nacimiento': date(2007, 1, 22),
        'contacto_emergencia': 'Papá: 895432109',
        'clase': cursos[0]  # Asignamos a la primera clase
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
        contacto_emergencia=data['contacto_emergencia'],
        clase=data['clase']
    )
    print(f"✅ Estudiante {usuario.nombre} {usuario.apellido_paterno} creado con contraseña '{password}'")

print("✅ Estudiantes creados")
