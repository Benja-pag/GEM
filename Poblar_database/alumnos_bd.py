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
    AuthUser, Usuario, Especialidad, Docente, Administrativo, Curso, Estudiante, EvaluacionBase, Asignatura, AsignaturaInscrita, AsignaturaImpartida
)

cursos = list(Curso.objects.all())

estudiantes_data = [
    # curso 1A:
    {
        'rut': '34567890', 'div': 'K',
        'nombre': 'Luis', 'apellido_paterno': 'Ramirez', 'apellido_materno': 'Soto',
        'correo': 'luis.ramirez@gem.cl', 'telefono': '333333333',
        'direccion': 'Pje. Los Robles 45', 'fecha_nacimiento': date(2008, 3, 15),
        'contacto_emergencia': 'Mama: 999999999',
        'curso': cursos[0],
        'password': 'lramirez'
    }, 
    {
        'rut': '12345678', 'div': '9',
        'nombre': 'Ana', 'apellido_paterno': 'Gonzalez', 'apellido_materno': 'Mendoza',
        'correo': 'ana.gonzalez@gem.cl', 'telefono': '912345678',
        'direccion': 'Av. Libertad 123', 'fecha_nacimiento': date(2005, 7, 20),
        'contacto_emergencia': 'Papa: 998877665',
        'curso': cursos[0],
        'password': 'agonzalez'
    },
    {
        'rut': '23456789', 'div': '1',
        'nombre': 'Carlos', 'apellido_paterno': 'Gatica', 'apellido_materno': 'Perez',
        'correo': 'carlos.gatica@gem.cl', 'telefono': '923456789',
        'direccion': 'Calle Falsa 742', 'fecha_nacimiento': date(2007, 11, 5),
        'contacto_emergencia': 'Hermano: 987654321',
        'curso': cursos[0],
        'password': 'cgatica'
    },
    {
        'rut': '34567901', 'div': '2',
        'nombre': 'Maria', 'apellido_paterno': 'Lopez', 'apellido_materno': 'Rojas',
        'correo': 'maria.lopez@gem.cl', 'telefono': '934567890',
        'direccion': 'Pasaje Luna 10', 'fecha_nacimiento': date(2006, 1, 10),
        'contacto_emergencia': 'Tia: 976543210',
        'curso': cursos[0],
        'password': 'mlopez'
    },
    {
        'rut': '45789021', 'div': '3',
        'nombre': 'Jorge', 'apellido_paterno': 'Torres', 'apellido_materno': 'Silva',
        'correo': 'jorge.torres@gem.cl', 'telefono': '945678901',
        'direccion': 'Av. Las Flores 55', 'fecha_nacimiento': date(2004, 5, 25),
        'contacto_emergencia': 'Mama: 965432109',
        'curso': cursos[0],
        'password': 'jtorres'
    },
    {
        'rut': '56789012', 'div': '4',
        'nombre': 'Valentina', 'apellido_paterno': 'Rivas', 'apellido_materno': 'Navarro',
        'correo': 'valentina.rivas@gem.cl', 'telefono': '956789012',
        'direccion': 'Calle Sol 200', 'fecha_nacimiento': date(2008, 9, 30),
        'contacto_emergencia': 'Papa: 954321098',
        'curso': cursos[0],
        'password': 'vrivas'
    },
    {
        'rut': '67890123', 'div': '5',
        'nombre': 'Sebastian', 'apellido_paterno': 'Mendoza', 'apellido_materno': 'Campos',
        'correo': 'sebastian.mendoza@gem.cl', 'telefono': '967890123',
        'direccion': 'Av. Las Palmas 77', 'fecha_nacimiento': date(2005, 12, 1),
        'contacto_emergencia': 'Mama: 943210987',
        'curso': cursos[0],
        'password': 'smendoza'
    },
    {
        'rut': '78901234', 'div': '6',
        'nombre': 'Camila', 'apellido_paterno': 'Lagos', 'apellido_materno': 'Ortiz',
        'correo': 'camila.lagos@gem.cl', 'telefono': '978901234',
        'direccion': 'Pje. La Reina 88', 'fecha_nacimiento': date(2007, 3, 14),
        'contacto_emergencia': 'Hermano: 932109876',
        'curso': cursos[0],
        'password': 'clagos'
    },
    {
        'rut': '89012345', 'div': '7',
        'nombre': 'Diego', 'apellido_paterno': 'Sanchez', 'apellido_materno': 'Munoz',
        'correo': 'diego.sanchez@gem.cl', 'telefono': '989012345',
        'direccion': 'Calle Norte 15', 'fecha_nacimiento': date(2006, 6, 22),
        'contacto_emergencia': 'Tia: 921098765',
        'curso': cursos[0],
        'password': 'dsanchez'
    },
    {
        'rut': '90123456', 'div': '8',
        'nombre': 'Isidora', 'apellido_paterno': 'Vega', 'apellido_materno': 'Salazar',
        'correo': 'isidora.vega@gem.cl', 'telefono': '990123456',
        'direccion': 'Av. Sur 101', 'fecha_nacimiento': date(2004, 8, 18),
        'contacto_emergencia': 'Papa: 910987654',
        'curso': cursos[0],
        'password': 'ivega'
    },
    {
        'rut': '11223344', 'div': 'K',
        'nombre': 'Felipe', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Guzman',
        'correo': 'felipe.rojasg@gem.cl', 'telefono': '901234567',
        'direccion': 'Pje. Los Cedros 9', 'fecha_nacimiento': date(2005, 2, 28),
        'contacto_emergencia': 'Mama: 909876543',
        'curso': cursos[0],
        'password': 'frojasg'
    },
    {
        'rut': '22334455', 'div': '1',
        'nombre': 'Martina', 'apellido_paterno': 'San martin', 'apellido_materno': 'Paz',
        'correo': 'martina.sanmartin@gem.cl', 'telefono': '912345678',
        'direccion': 'Calle Nueva 456', 'fecha_nacimiento': date(2007, 4, 7),
        'contacto_emergencia': 'Hermano: 908765432',
        'curso': cursos[0],
        'password': 'msanmartin'
    },
    {
        'rut': '33445566', 'div': '2',
        'nombre': 'Matias', 'apellido_paterno': 'Castillo', 'apellido_materno': 'Rios',
        'correo': 'matias.castillo@gem.cl', 'telefono': '923456789',
        'direccion': 'Av. Central 321', 'fecha_nacimiento': date(2006, 10, 9),
        'contacto_emergencia': 'Tia: 907654321',
        'curso': cursos[0],
        'password': 'mcastillo'
    },
    {
        'rut': '44556677', 'div': '3',
        'nombre': 'Lucia', 'apellido_paterno': 'Perez', 'apellido_materno': 'Vargas',
        'correo': 'lucia.perez@gem.cl', 'telefono': '934567890',
        'direccion': 'Pje. Las Violetas 14', 'fecha_nacimiento': date(2008, 12, 19),
        'contacto_emergencia': 'Papa: 906543210',
        'curso': cursos[0],
        'password': 'lperez'
    },
    {
        'rut': '55667788', 'div': '4',
        'nombre': 'Ignacio', 'apellido_paterno': 'Añasco', 'apellido_materno': 'Diaz',
        'correo': 'ignacio.añasco@gem.cl', 'telefono': '945678901',
        'direccion': 'Calle Sur 33', 'fecha_nacimiento': date(2005, 1, 3),
        'contacto_emergencia': 'Mama: 905432109',
        'curso': cursos[0],
        'password': 'iañasco'
    },
    {
        'rut': '66778899', 'div': '5',
        'nombre': 'Fernanda', 'apellido_paterno': 'Alvarez', 'apellido_materno': 'Castro',
        'correo': 'fernanda.alvarez@gem.cl', 'telefono': '956789012',
        'direccion': 'Av. Las Rosas 101', 'fecha_nacimiento': date(2007, 6, 27),
        'contacto_emergencia': 'Tia: 904321098',
        'curso': cursos[0],
        'password': 'falvarez'
    },
    {
        'rut': '77889900', 'div': '6',
        'nombre': 'Andres', 'apellido_paterno': 'Carrasco', 'apellido_materno': 'Espinoza',
        'correo': 'andres.carrasco@gem.cl', 'telefono': '967890123',
        'direccion': 'Calle Norte 123', 'fecha_nacimiento': date(2006, 3, 11),
        'contacto_emergencia': 'Mama: 903210987',
        'curso': cursos[0],
        'password': 'acarrasco'
    },
    {
        'rut': '88990011', 'div': '7',
        'nombre': 'Sofia', 'apellido_paterno': 'Gallardo', 'apellido_materno': 'Pizarro',
        'correo': 'sofia.gallardo@gem.cl', 'telefono': '978901234',
        'direccion': 'Pasaje Central 56', 'fecha_nacimiento': date(2005, 9, 5),
        'contacto_emergencia': 'Hermano: 902109876',
        'curso': cursos[0],
        'password': 'sgallardo'
    },
    {
        'rut': '99001122', 'div': '8',
        'nombre': 'Tomas', 'apellido_paterno': 'Aravena', 'apellido_materno': 'Saavedra',
        'correo': 'tomas.aravena@gem.cl', 'telefono': '989012345',
        'direccion': 'Av. Libertad 67', 'fecha_nacimiento': date(2008, 7, 8),
        'contacto_emergencia': 'Papa: 901098765',
        'curso': cursos[0],
        'password': 'taravena'
    },
    {
        'rut': '10111213', 'div': '9',
        'nombre': 'Antonia', 'apellido_paterno': 'Ortega', 'apellido_materno': 'Bravo',
        'correo': 'antonia.ortega@gem.cl', 'telefono': '990123456',
        'direccion': 'Pje. Las Palmas 8', 'fecha_nacimiento': date(2004, 10, 23),
        'contacto_emergencia': 'Mama: 900987654',
        'curso': cursos[0],
        'password': 'aortega'
    },
    #curso 1B:
    {
        'rut': '12131415', 'div': 'K',
        'nombre': 'Gabriel', 'apellido_paterno': 'Saez', 'apellido_materno': 'Alarcon',
        'correo': 'gabriel.saeza@gem.cl', 'telefono': '901234567',
        'direccion': 'Calle Estrella 90', 'fecha_nacimiento': date(2007, 2, 17),
        'contacto_emergencia': 'Papa: 899876543',
        'curso': cursos[1],
        'password': 'gsaez'
    },
    {
        'rut': '13141516', 'div': '1',
        'nombre': 'Isabel', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Nunez',
        'correo': 'isabel.rojasn@gem.cl', 'telefono': '912345678',
        'direccion': 'Av. Andes 321', 'fecha_nacimiento': date(2006, 11, 2),
        'contacto_emergencia': 'Hermana: 898765432',
        'curso': cursos[1],
        'password': 'irojasn'
    },

    {
        'rut': '14151617', 'div': '2',
        'nombre': 'Valentina', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Salazar',
        'correo': 'valentina.rojas.s@gem.cl', 'telefono': '923456789',
        'direccion': 'Pje. Sur 111', 'fecha_nacimiento': date(2007, 4, 25),
        'contacto_emergencia': 'Papa: 887654321',
        'curso': cursos[1],
        'password': 'vrojass'
    },
    {
        'rut': '15161718', 'div': '3',
        'nombre': 'Lucas', 'apellido_paterno': 'Araya', 'apellido_materno': 'Gomez',
        'correo': 'lucas.araya@gem.cl', 'telefono': '934567890',
        'direccion': 'Camino Viejo 33', 'fecha_nacimiento': date(2006, 12, 15),
        'contacto_emergencia': 'Mama: 876543210',
        'curso': cursos[1],
        'password': 'laraya'
    },
    {
        'rut': '16171819', 'div': '4',
        'nombre': 'Martina', 'apellido_paterno': 'Silva', 'apellido_materno': 'Venegas',
        'correo': 'martina.silvav@gem.cl', 'telefono': '945678901',
        'direccion': 'Av. Lomas 72', 'fecha_nacimiento': date(2005, 5, 3),
        'contacto_emergencia': 'Tia: 865432109',
        'curso': cursos[1],
        'password': 'msilvav'
    },
    # estudiantes 6:
    {
        'rut': '17181920', 'div': '5',
        'nombre': 'Benjamin', 'apellido_paterno': 'Vera', 'apellido_materno': 'Hidalgo',
        'correo': 'benjamin.vera@gem.cl', 'telefono': '956789012',
        'direccion': 'Villa Esperanza 9', 'fecha_nacimiento': date(2007, 8, 30),
        'contacto_emergencia': 'Abuela: 854321098',
        'curso': cursos[1],
        'password': 'bvera'
    },
    {
        'rut': '18192021', 'div': '6',
        'nombre': 'Camila', 'apellido_paterno': 'Fuentes', 'apellido_materno': 'Riquelme',
        'correo': 'camila.fuentesr@gem.cl', 'telefono': '967890123',
        'direccion': 'Calle Azul 45', 'fecha_nacimiento': date(2006, 1, 19),
        'contacto_emergencia': 'Mama: 843210987',
        'curso': cursos[1],
        'password': 'cfuentesr'
    },
    {
        'rut': '18203040', 'div': '1',
        'nombre': 'Benjamín', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Mella',
        'correo': 'benjamin.rojasM@gem.cl', 'telefono': '966123456',
        'direccion': 'Calle Verde 101', 'fecha_nacimiento': date(2006, 2, 15),
        'contacto_emergencia': 'Papa: 854321098',
        'curso': cursos[1],
        'password': 'brojas'
    },
    {
        'rut': '18203041', 'div': '2',
        'nombre': 'Valeria', 'apellido_paterno': 'Castillo', 'apellido_materno': 'Muñoz',
        'correo': 'valeria.castilloM@gem.cl', 'telefono': '967234567',
        'direccion': 'Calle Roja 32', 'fecha_nacimiento': date(2006, 3, 12),
        'contacto_emergencia': 'Mama: 864321987',
        'curso': cursos[1],
        'password': 'vcastillo'
    },
    {
        'rut': '18203042', 'div': '3',
        'nombre': 'Diego', 'apellido_paterno': 'Navarro', 'apellido_materno': 'Salinas',
        'correo': 'diego.navarrosa@gem.cl', 'telefono': '968345678',
        'direccion': 'Calle Amarilla 21', 'fecha_nacimiento': date(2006, 4, 8),
        'contacto_emergencia': 'Tío: 874321876',
        'curso': cursos[1],
        'password': 'dnavarros'
    },
    {
        'rut': '18203043', 'div': '4',
        'nombre': 'Florencia', 'apellido_paterno': 'Gallardo', 'apellido_materno': 'Vega',
        'correo': 'florencia.gallardoV@gem.cl', 'telefono': '969456789',
        'direccion': 'Calle Blanca 77', 'fecha_nacimiento': date(2006, 5, 2),
        'contacto_emergencia': 'Abuela: 884321765',
        'curso': cursos[1],
        'password': 'fgallardo'
    },
    {
        'rut': '18203044', 'div': '5',
        'nombre': 'Leonardo', 'apellido_paterno': 'Paredes', 'apellido_materno': 'Bravo',
        'correo': 'leonardo.paredesB@gem.cl', 'telefono': '961234567',
        'direccion': 'Calle Negra 98', 'fecha_nacimiento': date(2006, 6, 20),
        'contacto_emergencia': 'Hermana: 894321654',
        'curso': cursos[1],
        'password': 'lparedes'
    },
    {
        'rut': '18203045', 'div': '6',
        'nombre': 'Josefa', 'apellido_paterno': 'Fernández', 'apellido_materno': 'López',
        'correo': 'josefa.fernandezL@gem.cl', 'telefono': '962345678',
        'direccion': 'Calle Gris 12', 'fecha_nacimiento': date(2006, 7, 14),
        'contacto_emergencia': 'Papa: 904321543',
        'curso': cursos[1],
        'password': 'jfernandez'
    },
    {
        'rut': '18203046', 'div': '7',
        'nombre': 'Tomás', 'apellido_paterno': 'Silva', 'apellido_materno': 'Morales',
        'correo': 'tomas.silvaM@gem.cl', 'telefono': '963456789',
        'direccion': 'Calle Marfil 56', 'fecha_nacimiento': date(2006, 8, 30),
        'contacto_emergencia': 'Tía: 914321432',
        'curso': cursos[1],
        'password': 'tsilva'
    },
    {
        'rut': '18203047', 'div': '8',
        'nombre': 'Martina', 'apellido_paterno': 'Araya', 'apellido_materno': 'Campos',
        'correo': 'martina.arayaC@gem.cl', 'telefono': '964567890',
        'direccion': 'Calle Celeste 88', 'fecha_nacimiento': date(2006, 9, 5),
        'contacto_emergencia': 'Mama: 924321321',
        'curso': cursos[1],
        'password': 'maraya'
    },
    {
        'rut': '18203048', 'div': '9',
        'nombre': 'Ignacio', 'apellido_paterno': 'Cortés', 'apellido_materno': 'Henríquez',
        'correo': 'ignacio.cortesH@gem.cl', 'telefono': '965678901',
        'direccion': 'Calle Turquesa 19', 'fecha_nacimiento': date(2006, 10, 22),
        'contacto_emergencia': 'Abuelo: 934321210',
        'curso': cursos[1],
        'password': 'icortes'
    },
    {
        'rut': '18203049', 'div': '1',
        'nombre': 'Antonia', 'apellido_paterno': 'Saavedra', 'apellido_materno': 'Ortega',
        'correo': 'antonia.saavedraO@gem.cl', 'telefono': '966789012',
        'direccion': 'Calle Violeta 33', 'fecha_nacimiento': date(2006, 11, 17),
        'contacto_emergencia': 'Hermano: 944321109',
        'curso': cursos[1],
        'password': 'asaavedra'
    },
    {
        'rut': '18203050', 'div': '1',
        'nombre': 'Cristóbal', 'apellido_paterno': 'Venegas', 'apellido_materno': 'Zúñiga',
        'correo': 'cristobal.venegasZ@gem.cl', 'telefono': '967890123',
        'direccion': 'Calle Arena 50', 'fecha_nacimiento': date(2006, 12, 3),
        'contacto_emergencia': 'Tío: 954321098',
        'curso': cursos[1],
        'password': 'cvenegas'
    },
    {
        'rut': '18203051', 'div': '2',
        'nombre': 'Daniela', 'apellido_paterno': 'Mora', 'apellido_materno': 'Carrasco',
        'correo': 'daniela.moraC@gem.cl', 'telefono': '968901234',
        'direccion': 'Calle Sol 7', 'fecha_nacimiento': date(2007, 1, 10),
        'contacto_emergencia': 'Mama: 964321987',
        'curso': cursos[1],
        'password': 'dmora'
    },
    {
        'rut': '18203052', 'div': '3',
        'nombre': 'Vicente', 'apellido_paterno': 'Acuña', 'apellido_materno': 'Reyes',
        'correo': 'vicente.acunaR@gem.cl', 'telefono': '969012345',
        'direccion': 'Calle Bronce 61', 'fecha_nacimiento': date(2007, 2, 8),
        'contacto_emergencia': 'Papa: 974321876',
        'curso': cursos[1],
        'password': 'vacuna'
    },
    #curso 2A:
    {
    'rut': '18204001', 'div': '1',
    'nombre': 'Sofia', 'apellido_paterno': 'Ramirez', 'apellido_materno': 'Lopez',
    'correo': 'sofia.ramirezL@gem.cl', 'telefono': '970000001',
    'direccion': 'Calle Roble 12', 'fecha_nacimiento': date(2005, 3, 15),
    'contacto_emergencia': 'Mama: 940000001',
    'curso': cursos[2],
    'password': 'sramirez'
    },
    {
        'rut': '18204002', 'div': '2',
        'nombre': 'Benjamín', 'apellido_paterno': 'Ortiz', 'apellido_materno': 'Flores',
        'correo': 'benjamin.ortizF@gem.cl', 'telefono': '970000002',
        'direccion': 'Calle Cedro 24', 'fecha_nacimiento': date(2005, 6, 21),
        'contacto_emergencia': 'Papa: 940000002',
        'curso': cursos[2],
        'password': 'bortiz'
    },
    {
        'rut': '18204003', 'div': '3',
        'nombre': 'Isidora', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Vargas',
        'correo': 'isidora.rojasV@gem.cl', 'telefono': '970000003',
        'direccion': 'Calle Sauce 36', 'fecha_nacimiento': date(2005, 9, 10),
        'contacto_emergencia': 'Hermano: 940000003',
        'curso': cursos[2],
        'password': 'irojasv'
    },
    {
        'rut': '18204004', 'div': '4',
        'nombre': 'Matías', 'apellido_paterno': 'Salinas', 'apellido_materno': 'Cruz',
        'correo': 'matias.salinasc@gem.cl', 'telefono': '970000004',
        'direccion': 'Calle Laurel 48', 'fecha_nacimiento': date(2005, 12, 5),
        'contacto_emergencia': 'Tía: 940000004',
        'curso': cursos[2],
        'password': 'msalinasc'
    },
    {
        'rut': '18204005', 'div': '5',
        'nombre': 'Camila', 'apellido_paterno': 'Fuentes', 'apellido_materno': 'Pérez',
        'correo': 'camila.fuentesP@gem.cl', 'telefono': '970000005',
        'direccion': 'Calle Naranjo 60', 'fecha_nacimiento': date(2005, 2, 18),
        'contacto_emergencia': 'Mama: 940000005',
        'curso': cursos[2],
        'password': 'cfuentes'
    },
    {
        'rut': '18204006', 'div': '6',
        'nombre': 'Diego', 'apellido_paterno': 'Vidal', 'apellido_materno': 'Salazar',
        'correo': 'diego.vidalS@gem.cl', 'telefono': '970000006',
        'direccion': 'Calle Pino 72', 'fecha_nacimiento': date(2005, 7, 22),
        'contacto_emergencia': 'Papa: 940000006',
        'curso': cursos[2],
        'password': 'dvidal'
    },
    {
        'rut': '18204007', 'div': '7',
        'nombre': 'Fernanda', 'apellido_paterno': 'Gómez', 'apellido_materno': 'Rojas',
        'correo': 'fernanda.gomezr@gem.cl', 'telefono': '970000007',
        'direccion': 'Calle Olivo 84', 'fecha_nacimiento': date(2005, 4, 11),
        'contacto_emergencia': 'Hermana: 940000007',
        'curso': cursos[2],
        'password': 'fgomezr'
    },
    {
        'rut': '18204008', 'div': '8',
        'nombre': 'Sebastián', 'apellido_paterno': 'Herrera', 'apellido_materno': 'Muñoz',
        'correo': 'sebastian.herreram@gem.cl', 'telefono': '970000008',
        'direccion': 'Calle Laurel 96', 'fecha_nacimiento': date(2005, 11, 13),
        'contacto_emergencia': 'Tío: 940000008',
        'curso': cursos[2],
        'password': 'sherreram'
    },
    {
        'rut': '18204009', 'div': '9',
        'nombre': 'Antonia', 'apellido_paterno': 'Castillo', 'apellido_materno': 'Silva',
        'correo': 'antonia.castilloS@gem.cl', 'telefono': '970000009',
        'direccion': 'Calle Ciprés 108', 'fecha_nacimiento': date(2005, 5, 6),
        'contacto_emergencia': 'Mama: 940000009',
        'curso': cursos[2],
        'password': 'acastillo'
    },
    {
        'rut': '18204010', 'div': '1',
        'nombre': 'Gabriel', 'apellido_paterno': 'Navarro', 'apellido_materno': 'Herrera',
        'correo': 'gabriel.navarroH@gem.cl', 'telefono': '970000010',
        'direccion': 'Calle Roble 120', 'fecha_nacimiento': date(2005, 10, 25),
        'contacto_emergencia': 'Papa: 940000010',
        'curso': cursos[2],
        'password': 'gnavarro'
    },
    {
    'rut': '18204011', 'div': '1',
    'nombre': 'Valentina', 'apellido_paterno': 'Molina', 'apellido_materno': 'Lagos',
    'correo': 'valentina.molinaL@gem.cl', 'telefono': '970000011',
    'direccion': 'Calle Fresno 132', 'fecha_nacimiento': date(2005, 8, 30),
    'contacto_emergencia': 'Mama: 940000011',
    'curso': cursos[2],
    'password': 'vmolina'
    },
    {
        'rut': '18204012', 'div': '2',
        'nombre': 'Ignacio', 'apellido_paterno': 'Paredes', 'apellido_materno': 'Vega',
        'correo': 'ignacio.paredesv@gem.cl', 'telefono': '970000012',
        'direccion': 'Calle Lirio 144', 'fecha_nacimiento': date(2005, 1, 14),
        'contacto_emergencia': 'Papa: 940000012',
        'curso': cursos[2],
        'password': 'iparedesv'
    },
    {
        'rut': '18204013', 'div': '3',
        'nombre': 'Martina', 'apellido_paterno': 'Fuentes', 'apellido_materno': 'Reyes',
        'correo': 'martina.fuentesr@gem.cl', 'telefono': '970000013',
        'direccion': 'Calle Ciprés 156', 'fecha_nacimiento': date(2005, 9, 9),
        'contacto_emergencia': 'Hermana: 940000013',
        'curso': cursos[2],
        'password': 'mfuentesr'
    },
    {
        'rut': '18204014', 'div': '4',
        'nombre': 'Joaquín', 'apellido_paterno': 'Suárez', 'apellido_materno': 'Cárdenas',
        'correo': 'joaquin.suarezC@gem.cl', 'telefono': '970000014',
        'direccion': 'Calle Olmo 168', 'fecha_nacimiento': date(2005, 3, 28),
        'contacto_emergencia': 'Tío: 940000014',
        'curso': cursos[2],
        'password': 'jsuarez'
    },
    {
        'rut': '18204015', 'div': '5',
        'nombre': 'Natalia', 'apellido_paterno': 'Vargas', 'apellido_materno': 'Mora',
        'correo': 'natalia.vargasM@gem.cl', 'telefono': '970000015',
        'direccion': 'Calle Sauce 180', 'fecha_nacimiento': date(2005, 7, 19),
        'contacto_emergencia': 'Mama: 940000015',
        'curso': cursos[2],
        'password': 'nvargas'
    },
    {
        'rut': '18204016', 'div': '6',
        'nombre': 'Tomás', 'apellido_paterno': 'Reyes', 'apellido_materno': 'Pino',
        'correo': 'tomas.reyesP@gem.cl', 'telefono': '970000016',
        'direccion': 'Calle Roble 192', 'fecha_nacimiento': date(2005, 11, 2),
        'contacto_emergencia': 'Papa: 940000016',
        'curso': cursos[2],
        'password': 'treyes'
    },
    {
        'rut': '18204017', 'div': '6',
        'nombre': 'Catalina', 'apellido_paterno': 'Morales', 'apellido_materno': 'Espinoza',
        'correo': 'catalina.moralesE@gem.cl', 'telefono': '970000017',
        'direccion': 'Calle Laurel 204', 'fecha_nacimiento': date(2005, 5, 23),
        'contacto_emergencia': 'Hermana: 940000017',
        'curso': cursos[2],
        'password': 'cmorales'
    },
    {
        'rut': '18204018', 'div': '6',
        'nombre': 'Francisco', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Salas',
        'correo': 'francisco.rojasS@gem.cl', 'telefono': '970000018',
        'direccion': 'Calle Lirio 216', 'fecha_nacimiento': date(2005, 2, 6),
        'contacto_emergencia': 'Tío: 940000018',
        'curso': cursos[2],
        'password': 'frojas'
    },
    {
        'rut': '18204019', 'div': '9',
        'nombre': 'Paula', 'apellido_paterno': 'Silva', 'apellido_materno': 'Guzmán',
        'correo': 'paula.silvaG@gem.cl', 'telefono': '970000019',
        'direccion': 'Calle Naranjo 228', 'fecha_nacimiento': date(2005, 8, 14),
        'contacto_emergencia': 'Mama: 940000019',
        'curso': cursos[2],
        'password': 'psilva'
    },
    {
        'rut': '18204020', 'div': '5',
        'nombre': 'Lucas', 'apellido_paterno': 'Vargas', 'apellido_materno': 'Méndez',
        'correo': 'lucas.vargasM@gem.cl', 'telefono': '970000020',
        'direccion': 'Calle Pino 240', 'fecha_nacimiento': date(2005, 4, 27),
        'contacto_emergencia': 'Papa: 940000020',
        'curso': cursos[2],
        'password': 'lvargas'
    },
    #curso 2B:
    {
    'rut': '18205001', 'div': '1',
    'nombre': 'Diego', 'apellido_paterno': 'Contreras', 'apellido_materno': 'Rojas',
    'correo': 'diego.contrerasR@gem.cl', 'telefono': '971000001',
    'direccion': 'Calle Albahaca 12', 'fecha_nacimiento': date(2005, 6, 15),
    'contacto_emergencia': 'Mama: 941000001',
    'curso': cursos[3],
    'password': 'dcontreras'
    },
    {
        'rut': '18205002', 'div': '2',
        'nombre': 'Isidora', 'apellido_paterno': 'Campos', 'apellido_materno': 'Vargas',
        'correo': 'isidora.camposv@gem.cl', 'telefono': '971000002',
        'direccion': 'Calle Nuez 24', 'fecha_nacimiento': date(2005, 9, 21),
        'contacto_emergencia': 'Papa: 941000002',
        'curso': cursos[3],
        'password': 'icamposv'
    },
    {
        'rut': '18205003', 'div': '3',
        'nombre': 'Benjamín', 'apellido_paterno': 'López', 'apellido_materno': 'Araya',
        'correo': 'benjamin.lopezA@gem.cl', 'telefono': '971000003',
        'direccion': 'Calle Laurel 36', 'fecha_nacimiento': date(2005, 12, 3),
        'contacto_emergencia': 'Hermana: 941000003',
        'curso': cursos[3],
        'password': 'blopez'
    },
    {
        'rut': '18205004', 'div': '4',
        'nombre': 'Antonia', 'apellido_paterno': 'Muñoz', 'apellido_materno': 'Salazar',
        'correo': 'antonia.munozS@gem.cl', 'telefono': '971000004',
        'direccion': 'Calle Olivo 48', 'fecha_nacimiento': date(2005, 4, 10),
        'contacto_emergencia': 'Tío: 941000004',
        'curso': cursos[3],
        'password': 'amunoz'
    },
    {
        'rut': '18205005', 'div': '5',
        'nombre': 'Javier', 'apellido_paterno': 'Vidal', 'apellido_materno': 'Pérez',
        'correo': 'javier.vidalP@gem.cl', 'telefono': '971000005',
        'direccion': 'Calle Cerezo 60', 'fecha_nacimiento': date(2005, 3, 2),
        'contacto_emergencia': 'Mama: 941000005',
        'curso': cursos[3],
        'password': 'jvidal'
    },
    {
        'rut': '18205006', 'div': '6',
        'nombre': 'Camila', 'apellido_paterno': 'Silva', 'apellido_materno': 'Ortiz',
        'correo': 'camila.silvao@gem.cl', 'telefono': '971000006',
        'direccion': 'Calle Cedro 72', 'fecha_nacimiento': date(2005, 7, 28),
        'contacto_emergencia': 'Papa: 941000006',
        'curso': cursos[3],
        'password': 'csilvao'
    },
    {
        'rut': '18205007', 'div': '7',
        'nombre': 'Felipe', 'apellido_paterno': 'Castillo', 'apellido_materno': 'Navarro',
        'correo': 'felipe.castilloN@gem.cl', 'telefono': '971000007',
        'direccion': 'Calle Ciprés 84', 'fecha_nacimiento': date(2005, 8, 16),
        'contacto_emergencia': 'Hermana: 941000007',
        'curso': cursos[3],
        'password': 'fcastillo'
    },
    {
        'rut': '18205008', 'div': '8',
        'nombre': 'Francisca', 'apellido_paterno': 'Morales', 'apellido_materno': 'Espinoza',
        'correo': 'francisca.moralesE@gem.cl', 'telefono': '971000008',
        'direccion': 'Calle Sauce 96', 'fecha_nacimiento': date(2005, 11, 22),
        'contacto_emergencia': 'Tío: 941000008',
        'curso': cursos[3],
        'password': 'fmorales'
    },
    {
        'rut': '18205009', 'div': '9',
        'nombre': 'Santiago', 'apellido_paterno': 'Pérez', 'apellido_materno': 'Cruz',
        'correo': 'santiago.perezC@gem.cl', 'telefono': '971000009',
        'direccion': 'Calle Roble 108', 'fecha_nacimiento': date(2005, 5, 11),
        'contacto_emergencia': 'Mama: 941000009',
        'curso': cursos[3],
        'password': 'sperez'
    },
    {
        'rut': '18205010', 'div': '1',
        'nombre': 'María', 'apellido_paterno': 'Herrera', 'apellido_materno': 'Gómez',
        'correo': 'maria.herreraG@gem.cl', 'telefono': '971000010',
        'direccion': 'Calle Laurel 120', 'fecha_nacimiento': date(2005, 10, 19),
        'contacto_emergencia': 'Papa: 941000010',
        'curso': cursos[3],
        'password': 'mherrera'
    },
    {
    'rut': '18205011', 'div': '1',
    'nombre': 'Valentina', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Soto',
    'correo': 'valentina.rojasS@gem.cl', 'telefono': '971000011',
    'direccion': 'Calle Palma 132', 'fecha_nacimiento': date(2005, 2, 5),
    'contacto_emergencia': 'Mama: 941000011',
    'curso': cursos[3],
    'password': 'vrojas'
    },
    {
        'rut': '18205012', 'div': '2',
        'nombre': 'Matías', 'apellido_paterno': 'Silva', 'apellido_materno': 'Méndez',
        'correo': 'matias.silvaM@gem.cl', 'telefono': '971000012',
        'direccion': 'Calle Roble 144', 'fecha_nacimiento': date(2005, 8, 14),
        'contacto_emergencia': 'Papa: 941000012',
        'curso': cursos[3],
        'password': 'msilva'
    },
    {
        'rut': '18205013', 'div': '3',
        'nombre': 'Antonia', 'apellido_paterno': 'Lara', 'apellido_materno': 'Campos',
        'correo': 'antonia.laraC@gem.cl', 'telefono': '971000013',
        'direccion': 'Calle Nuez 156', 'fecha_nacimiento': date(2005, 4, 28),
        'contacto_emergencia': 'Hermano: 941000013',
        'curso': cursos[3],
        'password': 'alara'
    },
    {
        'rut': '18205014', 'div': '4',
        'nombre': 'Joaquín', 'apellido_paterno': 'Gómez', 'apellido_materno': 'Rivas',
        'correo': 'joaquin.gomezR@gem.cl', 'telefono': '971000014',
        'direccion': 'Calle Sauce 168', 'fecha_nacimiento': date(2005, 6, 1),
        'contacto_emergencia': 'Mama: 941000014',
        'curso': cursos[3],
        'password': 'jgomez'
    },
    {
        'rut': '18205015', 'div': '5',
        'nombre': 'Catalina', 'apellido_paterno': 'Vargas', 'apellido_materno': 'Sánchez',
        'correo': 'catalina.vargasS@gem.cl', 'telefono': '971000015',
        'direccion': 'Calle Ciprés 180', 'fecha_nacimiento': date(2005, 7, 20),
        'contacto_emergencia': 'Papa: 941000015',
        'curso': cursos[3],
        'password': 'cvargas'
    },
    {
        'rut': '18205016', 'div': '6',
        'nombre': 'Sebastián', 'apellido_paterno': 'Molina', 'apellido_materno': 'Ortiz',
        'correo': 'sebastian.molinaO@gem.cl', 'telefono': '971000016',
        'direccion': 'Calle Olivo 192', 'fecha_nacimiento': date(2005, 5, 25),
        'contacto_emergencia': 'Hermana: 941000016',
        'curso': cursos[3],
        'password': 'smolina'
    },
    {
        'rut': '18205017', 'div': '6',
        'nombre': 'Fernanda', 'apellido_paterno': 'Cruz', 'apellido_materno': 'Navarro',
        'correo': 'fernanda.cruzna@gem.cl', 'telefono': '971000017',
        'direccion': 'Calle Laurel 204', 'fecha_nacimiento': date(2005, 3, 18),
        'contacto_emergencia': 'Tío: 941000017',
        'curso': cursos[3],
        'password': 'fcruzn'
    },
    {
        'rut': '18205018', 'div': '6',
        'nombre': 'Ignacio', 'apellido_paterno': 'Herrera', 'apellido_materno': 'Pérez',
        'correo': 'ignacio.herrerape@gem.cl', 'telefono': '971000018',
        'direccion': 'Calle Cerezo 216', 'fecha_nacimiento': date(2005, 1, 30),
        'contacto_emergencia': 'Mama: 941000018',
        'curso': cursos[3],
        'password': 'iherrerap'
    },
    {
        'rut': '18205019', 'div': '9',
        'nombre': 'Paula', 'apellido_paterno': 'Fuentes', 'apellido_materno': 'Vargas',
        'correo': 'paula.fuentesva@gem.cl', 'telefono': '971000019',
        'direccion': 'Calle Azul 228', 'fecha_nacimiento': date(2005, 12, 9),
        'contacto_emergencia': 'Papa: 941000019',
        'curso': cursos[3],
        'password': 'pfuentesv'
    },
    {
        'rut': '18205020', 'div': '5',
        'nombre': 'Tomás', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Soto',
        'correo': 'tomas.rojasS@gem.cl', 'telefono': '971000020',
        'direccion': 'Calle Palma 240', 'fecha_nacimiento': date(2005, 11, 4),
        'contacto_emergencia': 'Hermana: 941000020',
        'curso': cursos[3],
        'password': 'trojas'
    },
    #curso 3A:
    {
        'rut': '18300001', 'div': '1',
        'nombre': 'Ignacio', 'apellido_paterno': 'Torres', 'apellido_materno': 'Vargas',
        'correo': 'ignacio.torresV@gem.cl', 'telefono': '972000001',
        'direccion': 'Calle Roble 101', 'fecha_nacimiento': date(2004, 3, 10),
        'contacto_emergencia': 'Mama: 942000001',
        'curso': cursos[4],
        'password': 'itorres'
    },
    {
        'rut': '18300002', 'div': '2',
        'nombre': 'María', 'apellido_paterno': 'Salinas', 'apellido_materno': 'Rojas',
        'correo': 'maria.salinasr@gem.cl', 'telefono': '972000002',
        'direccion': 'Calle Nuez 113', 'fecha_nacimiento': date(2004, 7, 24),
        'contacto_emergencia': 'Papa: 942000002',
        'curso': cursos[4],
        'password': 'msalinasr'
    },
    {
        'rut': '18300003', 'div': '3',
        'nombre': 'Fernando', 'apellido_paterno': 'Herrera', 'apellido_materno': 'Soto',
        'correo': 'fernando.herreraS@gem.cl', 'telefono': '972000003',
        'direccion': 'Calle Laurel 125', 'fecha_nacimiento': date(2004, 5, 17),
        'contacto_emergencia': 'Hermano: 942000003',
        'curso': cursos[4],
        'password': 'fherrera'
    },
    {
        'rut': '18300004', 'div': '4',
        'nombre': 'Camila', 'apellido_paterno': 'López', 'apellido_materno': 'Méndez',
        'correo': 'camila.lopezM@gem.cl', 'telefono': '972000004',
        'direccion': 'Calle Sauce 137', 'fecha_nacimiento': date(2004, 8, 9),
        'contacto_emergencia': 'Mama: 942000004',
        'curso': cursos[4],
        'password': 'clopez'
    },
    {
        'rut': '18300005', 'div': '5',
        'nombre': 'Luis', 'apellido_paterno': 'Molina', 'apellido_materno': 'Ortiz',
        'correo': 'luis.molinaO@gem.cl', 'telefono': '972000005',
        'direccion': 'Calle Ciprés 149', 'fecha_nacimiento': date(2004, 11, 30),
        'contacto_emergencia': 'Papa: 942000005',
        'curso': cursos[4],
        'password': 'lmolina'
    },
    {
        'rut': '18300006', 'div': '6',
        'nombre': 'Valentina', 'apellido_paterno': 'Gómez', 'apellido_materno': 'Rivas',
        'correo': 'valentina.gomezR@gem.cl', 'telefono': '972000006',
        'direccion': 'Calle Olivo 161', 'fecha_nacimiento': date(2004, 1, 4),
        'contacto_emergencia': 'Hermana: 942000006',
        'curso': cursos[4],
        'password': 'vgomez'
    },
    {
        'rut': '18300007', 'div': '7',
        'nombre': 'Sebastián', 'apellido_paterno': 'Vargas', 'apellido_materno': 'Sánchez',
        'correo': 'sebastian.vargasS@gem.cl', 'telefono': '972000007',
        'direccion': 'Calle Laurel 173', 'fecha_nacimiento': date(2004, 9, 12),
        'contacto_emergencia': 'Mama: 942000007',
        'curso': cursos[4],
        'password': 'svargas'
    },
    {
        'rut': '18300008', 'div': '8',
        'nombre': 'Fernanda', 'apellido_paterno': 'Cruz', 'apellido_materno': 'Navarro',
        'correo': 'fernanda.cruzN@gem.cl', 'telefono': '972000008',
        'direccion': 'Calle Cerezo 185', 'fecha_nacimiento': date(2004, 6, 22),
        'contacto_emergencia': 'Papa: 942000008',
        'curso': cursos[4],
        'password': 'fcruz'
    },
    {
        'rut': '18300009', 'div': '9',
        'nombre': 'Ignacio', 'apellido_paterno': 'Herrera', 'apellido_materno': 'Pérez',
        'correo': 'ignacio.herreraP@gem.cl', 'telefono': '972000009',
        'direccion': 'Calle Olmo 197', 'fecha_nacimiento': date(2004, 4, 16),
        'contacto_emergencia': 'Hermano: 942000009',
        'curso': cursos[4],
        'password': 'iherrera'
    },
    {
        'rut': '18300010', 'div': '1',
        'nombre': 'Paula', 'apellido_paterno': 'Fuentes', 'apellido_materno': 'Vargas',
        'correo': 'paula.fuentesV@gem.cl', 'telefono': '972000010',
        'direccion': 'Calle Azul 209', 'fecha_nacimiento': date(2004, 2, 8),
        'contacto_emergencia': 'Mama: 942000010',
        'curso': cursos[4],
        'password': 'pfuentes'
    },
    {
    'rut': '18300011', 'div': '1',
    'nombre': 'Matías', 'apellido_paterno': 'Castro', 'apellido_materno': 'García',
    'correo': 'matias.castroG@gem.cl', 'telefono': '972000011',
    'direccion': 'Calle Fresno 221', 'fecha_nacimiento': date(2004, 10, 2),
    'contacto_emergencia': 'Papa: 942000011',
    'curso': cursos[4],
    'password': 'mcastro'
    },
    {
        'rut': '18300012', 'div': '2',
        'nombre': 'Sofía', 'apellido_paterno': 'Morales', 'apellido_materno': 'Alvarez',
        'correo': 'sofia.moralesA@gem.cl', 'telefono': '972000012',
        'direccion': 'Calle Lila 233', 'fecha_nacimiento': date(2004, 12, 14),
        'contacto_emergencia': 'Mama: 942000012',
        'curso': cursos[4],
        'password': 'smorales'
    },
    {
        'rut': '18300013', 'div': '3',
        'nombre': 'Diego', 'apellido_paterno': 'Ruiz', 'apellido_materno': 'Salazar',
        'correo': 'diego.ruizS@gem.cl', 'telefono': '972000013',
        'direccion': 'Calle Cedro 245', 'fecha_nacimiento': date(2004, 7, 7),
        'contacto_emergencia': 'Papa: 942000013',
        'curso': cursos[4],
        'password': 'druiz'
    },
    {
        'rut': '18300014', 'div': '4',
        'nombre': 'Isidora', 'apellido_paterno': 'Pérez', 'apellido_materno': 'Campos',
        'correo': 'isidora.perezca@gem.cl', 'telefono': '972000014',
        'direccion': 'Calle Sauce 257', 'fecha_nacimiento': date(2004, 11, 25),
        'contacto_emergencia': 'Mama: 942000014',
        'curso': cursos[4],
        'password': 'iperezca'
    },
    {
        'rut': '18300015', 'div': '5',
        'nombre': 'Jorge', 'apellido_paterno': 'Castillo', 'apellido_materno': 'Vega',
        'correo': 'jorge.castilloV@gem.cl', 'telefono': '972000015',
        'direccion': 'Calle Roble 269', 'fecha_nacimiento': date(2004, 5, 19),
        'contacto_emergencia': 'Papa: 942000015',
        'curso': cursos[4],
        'password': 'jcastillo'
    },
    {
        'rut': '18300016', 'div': '6',
        'nombre': 'Natalia', 'apellido_paterno': 'Soto', 'apellido_materno': 'Muñoz',
        'correo': 'natalia.sotoM@gem.cl', 'telefono': '972000016',
        'direccion': 'Calle Nuez 281', 'fecha_nacimiento': date(2004, 3, 3),
        'contacto_emergencia': 'Mama: 942000016',
        'curso': cursos[4],
        'password': 'nsoto'
    },
    {
        'rut': '18300017', 'div': '6',
        'nombre': 'Andrés', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Díaz',
        'correo': 'andres.rojasd@gem.cl', 'telefono': '972000017',
        'direccion': 'Calle Ciprés 293', 'fecha_nacimiento': date(2004, 6, 15),
        'contacto_emergencia': 'Papa: 942000017',
        'curso': cursos[4],
        'password': 'arojasd'
    },
    {
        'rut': '18300018', 'div': '6',
        'nombre': 'Catalina', 'apellido_paterno': 'Ortiz', 'apellido_materno': 'Salinas',
        'correo': 'catalina.ortizS@gem.cl', 'telefono': '972000018',
        'direccion': 'Calle Olivo 305', 'fecha_nacimiento': date(2004, 8, 27),
        'contacto_emergencia': 'Mama: 942000018',
        'curso': cursos[4],
        'password': 'cortiz'
    },
    {
        'rut': '18300019', 'div': '9',
        'nombre': 'Felipe', 'apellido_paterno': 'Gutiérrez', 'apellido_materno': 'Morales',
        'correo': 'felipe.gutierrezM@gem.cl', 'telefono': '972000019',
        'direccion': 'Calle Laurel 317', 'fecha_nacimiento': date(2004, 9, 9),
        'contacto_emergencia': 'Papa: 942000019',
        'curso': cursos[4],
        'password': 'fgutierrez'
    },
    {
        'rut': '18300020', 'div': '5',
        'nombre': 'Antonia', 'apellido_paterno': 'Vargas', 'apellido_materno': 'Rojas',
        'correo': 'antonia.vargasr@gem.cl', 'telefono': '972000020',
        'direccion': 'Calle Cerezo 329', 'fecha_nacimiento': date(2004, 12, 21),
        'contacto_emergencia': 'Mama: 942000020',
        'curso': cursos[4],
        'password': 'avargasr'
    },
    #curso 3:
    {
    'rut': '18400001', 'div': '1',
    'nombre': 'Lucas', 'apellido_paterno': 'Martínez', 'apellido_materno': 'López',
    'correo': 'lucas.martinezL@gem.cl', 'telefono': '973000001',
    'direccion': 'Calle Lirio 101', 'fecha_nacimiento': date(2004, 4, 5),
    'contacto_emergencia': 'Mama: 943000001',
    'curso': cursos[5],
    'password': 'lmartinez'
    },
    {
        'rut': '18400002', 'div': '2',
        'nombre': 'Valentina', 'apellido_paterno': 'González', 'apellido_materno': 'Paredes',
        'correo': 'valentina.gonzalezP@gem.cl', 'telefono': '973000002',
        'direccion': 'Calle Azucena 113', 'fecha_nacimiento': date(2004, 7, 19),
        'contacto_emergencia': 'Papa: 943000002',
        'curso': cursos[5],
        'password': 'vgonzalez'
    },
    {
        'rut': '18400003', 'div': '3',
        'nombre': 'Diego', 'apellido_paterno': 'Navarro', 'apellido_materno': 'Salazar',
        'correo': 'diego.navarroS@gem.cl', 'telefono': '973000003',
        'direccion': 'Calle Clavel 125', 'fecha_nacimiento': date(2004, 2, 28),
        'contacto_emergencia': 'Mama: 943000003',
        'curso': cursos[5],
        'password': 'dnavarro'
    },
    {
        'rut': '18400004', 'div': '4',
        'nombre': 'Isabella', 'apellido_paterno': 'Campos', 'apellido_materno': 'Rojas',
        'correo': 'isabella.camposR@gem.cl', 'telefono': '973000004',
        'direccion': 'Calle Dalia 137', 'fecha_nacimiento': date(2004, 9, 12),
        'contacto_emergencia': 'Papa: 943000004',
        'curso': cursos[5],
        'password': 'icampos'
    },
    {
        'rut': '18400005', 'div': '5',
        'nombre': 'Javier', 'apellido_paterno': 'Soto', 'apellido_materno': 'Muñoz',
        'correo': 'javier.sotoM@gem.cl', 'telefono': '973000005',
        'direccion': 'Calle Tulipán 149', 'fecha_nacimiento': date(2004, 3, 23),
        'contacto_emergencia': 'Mama: 943000005',
        'curso': cursos[5],
        'password': 'jsoto'
    },
    {
        'rut': '18400006', 'div': '6',
        'nombre': 'Natalia', 'apellido_paterno': 'Rivas', 'apellido_materno': 'Díaz',
        'correo': 'natalia.rivasD@gem.cl', 'telefono': '973000006',
        'direccion': 'Calle Margarita 161', 'fecha_nacimiento': date(2004, 6, 30),
        'contacto_emergencia': 'Papa: 943000006',
        'curso': cursos[5],
        'password': 'nrivas'
    },
    {
        'rut': '18400007', 'div': '7',
        'nombre': 'Andrés', 'apellido_paterno': 'Olivares', 'apellido_materno': 'Salinas',
        'correo': 'andres.olivaresS@gem.cl', 'telefono': '973000007',
        'direccion': 'Calle Gardenia 173', 'fecha_nacimiento': date(2004, 11, 8),
        'contacto_emergencia': 'Mama: 943000007',
        'curso': cursos[5],
        'password': 'aolivares'
    },
    {
        'rut': '18400008', 'div': '8',
        'nombre': 'Catalina', 'apellido_paterno': 'Muñoz', 'apellido_materno': 'Vega',
        'correo': 'catalina.munozV@gem.cl', 'telefono': '973000008',
        'direccion': 'Calle Jacarandá 185', 'fecha_nacimiento': date(2004, 1, 15),
        'contacto_emergencia': 'Papa: 943000008',
        'curso': cursos[5],
        'password': 'cmunoz'
    },
    {
        'rut': '18400009', 'div': '9',
        'nombre': 'Felipe', 'apellido_paterno': 'Gómez', 'apellido_materno': 'Morales',
        'correo': 'felipe.gomezM@gem.cl', 'telefono': '973000009',
        'direccion': 'Calle Lila 197', 'fecha_nacimiento': date(2004, 8, 24),
        'contacto_emergencia': 'Mama: 943000009',
        'curso': cursos[5],
        'password': 'fgomez'
    },
    {
        'rut': '18400010', 'div': '1',
        'nombre': 'Antonia', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Silva',
        'correo': 'antonia.rojasS@gem.cl', 'telefono': '973000010',
        'direccion': 'Calle Azalea 209', 'fecha_nacimiento': date(2004, 5, 4),
        'contacto_emergencia': 'Papa: 943000010',
        'curso': cursos[5],
        'password': 'arojas'
    },
    {
    'rut': '18400011', 'div': '1',
    'nombre': 'Martín', 'apellido_paterno': 'Vargas', 'apellido_materno': 'Espinoza',
    'correo': 'martin.vargasE@gem.cl', 'telefono': '973000011',
    'direccion': 'Calle Camelia 221', 'fecha_nacimiento': date(2004, 10, 7),
    'contacto_emergencia': 'Mama: 943000011',
    'curso': cursos[5],
    'password': 'mvargas'
    },
    {
        'rut': '18400012', 'div': '2',
        'nombre': 'Sofía', 'apellido_paterno': 'Herrera', 'apellido_materno': 'Castillo',
        'correo': 'sofia.herreraC@gem.cl', 'telefono': '973000012',
        'direccion': 'Calle Magnolia 233', 'fecha_nacimiento': date(2004, 12, 18),
        'contacto_emergencia': 'Papa: 943000012',
        'curso': cursos[5],
        'password': 'sherrera'
    },
    {
        'rut': '18400013', 'div': '3',
        'nombre': 'Tomás', 'apellido_paterno': 'Lara', 'apellido_materno': 'Pinto',
        'correo': 'tomas.laraP@gem.cl', 'telefono': '973000013',
        'direccion': 'Calle Diente de León 245', 'fecha_nacimiento': date(2004, 3, 3),
        'contacto_emergencia': 'Mama: 943000013',
        'curso': cursos[5],
        'password': 'tlara'
    },
    {
        'rut': '18400014', 'div': '4',
        'nombre': 'Fernanda', 'apellido_paterno': 'Miranda', 'apellido_materno': 'Flores',
        'correo': 'fernanda.mirandaF@gem.cl', 'telefono': '973000014',
        'direccion': 'Calle Pensamiento 257', 'fecha_nacimiento': date(2004, 6, 25),
        'contacto_emergencia': 'Papa: 943000014',
        'curso': cursos[5],
        'password': 'fmiranda'
    },
    {
        'rut': '18400015', 'div': '5',
        'nombre': 'Ignacio', 'apellido_paterno': 'Paredes', 'apellido_materno': 'Sánchez',
        'correo': 'ignacio.paredesS@gem.cl', 'telefono': '973000015',
        'direccion': 'Calle Violeta 269', 'fecha_nacimiento': date(2004, 8, 9),
        'contacto_emergencia': 'Mama: 943000015',
        'curso': cursos[5],
        'password': 'iparedes'
    },
    {
        'rut': '18400016', 'div': '6',
        'nombre': 'María José', 'apellido_paterno': 'Riquelme', 'apellido_materno': 'Ortiz',
        'correo': 'mariajose.riquelmeO@gem.cl', 'telefono': '973000016',
        'direccion': 'Calle Pensamiento 281', 'fecha_nacimiento': date(2004, 9, 29),
        'contacto_emergencia': 'Papa: 943000016',
        'curso': cursos[5],
        'password': 'mriquelme'
    },
    {
        'rut': '18400017', 'div': '6',
        'nombre': 'Diego', 'apellido_paterno': 'Salazar', 'apellido_materno': 'Méndez',
        'correo': 'diego.salazarM@gem.cl', 'telefono': '973000017',
        'direccion': 'Calle Margarita 293', 'fecha_nacimiento': date(2004, 11, 13),
        'contacto_emergencia': 'Mama: 943000017',
        'curso': cursos[5],
        'password': 'dsalazar'
    },
    {
        'rut': '18400018', 'div': '6',
        'nombre': 'Catalina', 'apellido_paterno': 'Silva', 'apellido_materno': 'Romero',
        'correo': 'catalina.silvaR@gem.cl', 'telefono': '973000018',
        'direccion': 'Calle Rosal 305', 'fecha_nacimiento': date(2004, 4, 22),
        'contacto_emergencia': 'Papa: 943000018',
        'curso': cursos[5],
        'password': 'csilva'
    },
    {
        'rut': '18400019', 'div': '9',
        'nombre': 'Sebastián', 'apellido_paterno': 'Vega', 'apellido_materno': 'Moreno',
        'correo': 'sebastian.vegaM@gem.cl', 'telefono': '973000019',
        'direccion': 'Calle Jazmín 317', 'fecha_nacimiento': date(2004, 7, 7),
        'contacto_emergencia': 'Mama: 943000019',
        'curso': cursos[5],
        'password': 'svega'
    },
    {
        'rut': '18400020', 'div': '5',
        'nombre': 'Paula', 'apellido_paterno': 'Valdés', 'apellido_materno': 'Lara',
        'correo': 'paula.valdesL@gem.cl', 'telefono': '973000020',
        'direccion': 'Calle Clavel 329', 'fecha_nacimiento': date(2004, 9, 18),
        'contacto_emergencia': 'Papa: 943000020',
        'curso': cursos[5],
        'password': 'pvaldes'
    },
    #curso 4A:
    {
    'rut': '18500001', 'div': '1',
    'nombre': 'Valentina', 'apellido_paterno': 'Morales', 'apellido_materno': 'Fuentes',
    'correo': 'valentina.moralesF@gem.cl', 'telefono': '974000001',
    'direccion': 'Calle Tulipán 12', 'fecha_nacimiento': date(2003, 5, 14),
    'contacto_emergencia': 'Mama: 954000001',
    'curso': cursos[6],
    'password': 'vmorales'
    },
    {
        'rut': '18500002', 'div': '2',
        'nombre': 'Lucas', 'apellido_paterno': 'Campos', 'apellido_materno': 'Rojas',
        'correo': 'lucas.camposR@gem.cl', 'telefono': '974000002',
        'direccion': 'Calle Orquídea 24', 'fecha_nacimiento': date(2003, 8, 30),
        'contacto_emergencia': 'Papa: 954000002',
        'curso': cursos[6],
        'password': 'lcampos'
    },
    {
        'rut': '18500003', 'div': '3',
        'nombre': 'Antonia', 'apellido_paterno': 'Soto', 'apellido_materno': 'Molina',
        'correo': 'antonia.sotoM@gem.cl', 'telefono': '974000003',
        'direccion': 'Calle Jazmín 36', 'fecha_nacimiento': date(2003, 3, 22),
        'contacto_emergencia': 'Mama: 954000003',
        'curso': cursos[6],
        'password': 'asoto'
    },
    {
        'rut': '18500004', 'div': '4',
        'nombre': 'Diego', 'apellido_paterno': 'Alarcón', 'apellido_materno': 'Salinas',
        'correo': 'diego.alarconS@gem.cl', 'telefono': '974000004',
        'direccion': 'Calle Margarita 48', 'fecha_nacimiento': date(2003, 11, 2),
        'contacto_emergencia': 'Papa: 954000004',
        'curso': cursos[6],
        'password': 'dalarcon'
    },
    {
        'rut': '18500005', 'div': '5',
        'nombre': 'Camila', 'apellido_paterno': 'Navarro', 'apellido_materno': 'Pérez',
        'correo': 'camila.navarroP@gem.cl', 'telefono': '974000005',
        'direccion': 'Calle Gardenia 50', 'fecha_nacimiento': date(2003, 7, 19),
        'contacto_emergencia': 'Mama: 954000005',
        'curso': cursos[6],
        'password': 'cnavarro'
    },
    {
        'rut': '18500006', 'div': '6',
        'nombre': 'Matías', 'apellido_paterno': 'Cortés', 'apellido_materno': 'Vargas',
        'correo': 'matias.cortesV@gem.cl', 'telefono': '974000006',
        'direccion': 'Calle Lirio 62', 'fecha_nacimiento': date(2003, 1, 15),
        'contacto_emergencia': 'Papa: 954000006',
        'curso': cursos[6],
        'password': 'mcortes'
    },
    {
        'rut': '18500007', 'div': '7',
        'nombre': 'Isidora', 'apellido_paterno': 'Pérez', 'apellido_materno': 'Castillo',
        'correo': 'isidora.perezC@gem.cl', 'telefono': '974000007',
        'direccion': 'Calle Orquídea 74', 'fecha_nacimiento': date(2003, 6, 11),
        'contacto_emergencia': 'Mama: 954000007',
        'curso': cursos[6],
        'password': 'iperezc'
    },
    {
        'rut': '18500008', 'div': '8',
        'nombre': 'Joaquín', 'apellido_paterno': 'Fuentes', 'apellido_materno': 'Riquelme',
        'correo': 'joaquin.fuentesR@gem.cl', 'telefono': '974000008',
        'direccion': 'Calle Tulipán 86', 'fecha_nacimiento': date(2003, 10, 29),
        'contacto_emergencia': 'Papa: 954000008',
        'curso': cursos[6],
        'password': 'jfuentes'
    },
    {
        'rut': '18500009', 'div': '9',
        'nombre': 'Natalia', 'apellido_paterno': 'Sánchez', 'apellido_materno': 'López',
        'correo': 'natalia.sanchezL@gem.cl', 'telefono': '974000009',
        'direccion': 'Calle Gardenia 98', 'fecha_nacimiento': date(2003, 12, 17),
        'contacto_emergencia': 'Mama: 954000009',
        'curso': cursos[6],
        'password': 'nsanchez'
    },
    {
        'rut': '18500010', 'div': '1',
        'nombre': 'Gabriel', 'apellido_paterno': 'Mendoza', 'apellido_materno': 'Soto',
        'correo': 'gabriel.mendozaS@gem.cl', 'telefono': '974000010',
        'direccion': 'Calle Margarita 110', 'fecha_nacimiento': date(2003, 4, 4),
        'contacto_emergencia': 'Papa: 954000010',
        'curso': cursos[6],
        'password': 'gmendoza'
    },
    {
    'rut': '18500011', 'div': '1',
    'nombre': 'Sofía', 'apellido_paterno': 'Rivas', 'apellido_materno': 'Gómez',
    'correo': 'sofia.rivasG@gem.cl', 'telefono': '974000011',
    'direccion': 'Calle Jazmín 122', 'fecha_nacimiento': date(2003, 9, 7),
    'contacto_emergencia': 'Mama: 954000011',
    'curso': cursos[6],
    'password': 'srivas'
    },
    {
        'rut': '18500012', 'div': '2',
        'nombre': 'Tomás', 'apellido_paterno': 'Herrera', 'apellido_materno': 'Cruz',
        'correo': 'tomas.herreraC@gem.cl', 'telefono': '974000012',
        'direccion': 'Calle Lirio 134', 'fecha_nacimiento': date(2003, 2, 18),
        'contacto_emergencia': 'Papa: 954000012',
        'curso': cursos[6],
        'password': 'therrera'
    },
    {
        'rut': '18500013', 'div': '3',
        'nombre': 'Fernanda', 'apellido_paterno': 'Castro', 'apellido_materno': 'Maldonado',
        'correo': 'fernanda.castroM@gem.cl', 'telefono': '974000013',
        'direccion': 'Calle Orquídea 146', 'fecha_nacimiento': date(2003, 6, 23),
        'contacto_emergencia': 'Mama: 954000013',
        'curso': cursos[6],
        'password': 'fcastro'
    },
    {
        'rut': '18500014', 'div': '4',
        'nombre': 'Benjamín', 'apellido_paterno': 'Vega', 'apellido_materno': 'Luna',
        'correo': 'benjamin.vegaL@gem.cl', 'telefono': '974000014',
        'direccion': 'Calle Tulipán 158', 'fecha_nacimiento': date(2003, 7, 30),
        'contacto_emergencia': 'Papa: 954000014',
        'curso': cursos[6],
        'password': 'bvega'
    },
    {
        'rut': '18500015', 'div': '5',
        'nombre': 'Camila', 'apellido_paterno': 'Mora', 'apellido_materno': 'Silva',
        'correo': 'camila.moraS@gem.cl', 'telefono': '974000015',
        'direccion': 'Calle Gardenia 170', 'fecha_nacimiento': date(2003, 5, 6),
        'contacto_emergencia': 'Mama: 954000015',
        'curso': cursos[6],
        'password': 'cmora'
    },
    {
        'rut': '18500016', 'div': '6',
        'nombre': 'Ignacio', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Alarcón',
        'correo': 'ignacio.rojasA@gem.cl', 'telefono': '974000016',
        'direccion': 'Calle Margarita 182', 'fecha_nacimiento': date(2003, 3, 29),
        'contacto_emergencia': 'Papa: 954000016',
        'curso': cursos[6],
        'password': 'irojas'
    },
    {
        'rut': '18500017', 'div': '6',
        'nombre': 'Martina', 'apellido_paterno': 'Salinas', 'apellido_materno': 'Ortiz',
        'correo': 'martina.salinasO@gem.cl', 'telefono': '974000017',
        'direccion': 'Calle Jazmín 194', 'fecha_nacimiento': date(2003, 1, 12),
        'contacto_emergencia': 'Mama: 954000017',
        'curso': cursos[6],
        'password': 'msalinas'
    },
    {
        'rut': '18500018', 'div': '6',
        'nombre': 'Sebastián', 'apellido_paterno': 'Torres', 'apellido_materno': 'Paredes',
        'correo': 'sebastian.torresP@gem.cl', 'telefono': '974000018',
        'direccion': 'Calle Lirio 206', 'fecha_nacimiento': date(2003, 9, 21),
        'contacto_emergencia': 'Papa: 954000018',
        'curso': cursos[6],
        'password': 'storres'
    },
    {
        'rut': '18500019', 'div': '9',
        'nombre': 'Agustina', 'apellido_paterno': 'Vargas', 'apellido_materno': 'Soto',
        'correo': 'agustina.vargasS@gem.cl', 'telefono': '974000019',
        'direccion': 'Calle Orquídea 218', 'fecha_nacimiento': date(2003, 11, 14),
        'contacto_emergencia': 'Mama: 954000019',
        'curso': cursos[6],
        'password': 'avargas'
    },
    {
        'rut': '18500020', 'div': '5',
        'nombre': 'Javier', 'apellido_paterno': 'López', 'apellido_materno': 'Campos',
        'correo': 'javier.lopezC@gem.cl', 'telefono': '974000020',
        'direccion': 'Calle Tulipán 230', 'fecha_nacimiento': date(2003, 4, 28),
        'contacto_emergencia': 'Papa: 954000020',
        'curso': cursos[6],
        'password': 'jlopez'
    },
    #curso 4B:
    {
    'rut': '18600001', 'div': '1',
    'nombre': 'Isidora', 'apellido_paterno': 'Castillo', 'apellido_materno': 'Morales',
    'correo': 'isidora.castilloM@gem.cl', 'telefono': '975000001',
    'direccion': 'Calle Margarita 12', 'fecha_nacimiento': date(2003, 10, 15),
    'contacto_emergencia': 'Mama: 955000001',
    'curso': cursos[7],
    'password': 'icastillo'
    },
    {
        'rut': '18600002', 'div': '2',
        'nombre': 'Diego', 'apellido_paterno': 'Fuentes', 'apellido_materno': 'Pérez',
        'correo': 'diego.fuentesP@gem.cl', 'telefono': '975000002',
        'direccion': 'Calle Lirio 34', 'fecha_nacimiento': date(2003, 7, 19),
        'contacto_emergencia': 'Papa: 955000002',
        'curso': cursos[7],
        'password': 'dfuentes'
    },
    {
        'rut': '18600003', 'div': '3',
        'nombre': 'Valentina', 'apellido_paterno': 'Navarro', 'apellido_materno': 'Reyes',
        'correo': 'valentina.navarroR@gem.cl', 'telefono': '975000003',
        'direccion': 'Calle Jazmín 56', 'fecha_nacimiento': date(2003, 3, 11),
        'contacto_emergencia': 'Mama: 955000003',
        'curso': cursos[7],
        'password': 'vnavarro'
    },
    {
        'rut': '18600004', 'div': '4',
        'nombre': 'Matías', 'apellido_paterno': 'Soto', 'apellido_materno': 'Vargas',
        'correo': 'matias.sotoV@gem.cl', 'telefono': '975000004',
        'direccion': 'Calle Gardenia 78', 'fecha_nacimiento': date(2003, 12, 29),
        'contacto_emergencia': 'Papa: 955000004',
        'curso': cursos[7],
        'password': 'msoto'
    },
    {
        'rut': '18600005', 'div': '5',
        'nombre': 'Camila', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Cruz',
        'correo': 'camila.rojasC@gem.cl', 'telefono': '975000005',
        'direccion': 'Calle Orquídea 90', 'fecha_nacimiento': date(2003, 6, 23),
        'contacto_emergencia': 'Mama: 955000005',
        'curso': cursos[7],
        'password': 'crojas'
    },
    {
        'rut': '18600006', 'div': '6',
        'nombre': 'Joaquín', 'apellido_paterno': 'Valenzuela', 'apellido_materno': 'Lara',
        'correo': 'joaquin.valenzuelaL@gem.cl', 'telefono': '975000006',
        'direccion': 'Calle Tulipán 102', 'fecha_nacimiento': date(2003, 1, 4),
        'contacto_emergencia': 'Papa: 955000006',
        'curso': cursos[7],
        'password': 'jvalenzuela'
    },
    {
        'rut': '18600007', 'div': '7',
        'nombre': 'Antonia', 'apellido_paterno': 'Salazar', 'apellido_materno': 'Olivares',
        'correo': 'antonia.salazarO@gem.cl', 'telefono': '975000007',
        'direccion': 'Calle Margarita 114', 'fecha_nacimiento': date(2003, 8, 16),
        'contacto_emergencia': 'Mama: 955000007',
        'curso': cursos[7],
        'password': 'asalazar'
    },
    {
        'rut': '18600008', 'div': '8',
        'nombre': 'Gabriel', 'apellido_paterno': 'Morales', 'apellido_materno': 'Pinto',
        'correo': 'gabriel.moralesP@gem.cl', 'telefono': '975000008',
        'direccion': 'Calle Lirio 126', 'fecha_nacimiento': date(2003, 4, 25),
        'contacto_emergencia': 'Papa: 955000008',
        'curso': cursos[7],
        'password': 'gmorales'
    },
    {
        'rut': '18600009', 'div': '9',
        'nombre': 'Isabel', 'apellido_paterno': 'Silva', 'apellido_materno': 'Herrera',
        'correo': 'isabel.silvaH@gem.cl', 'telefono': '975000009',
        'direccion': 'Calle Jazmín 138', 'fecha_nacimiento': date(2003, 11, 2),
        'contacto_emergencia': 'Mama: 955000009',
        'curso': cursos[7],
        'password': 'isilva'
    },
    {
        'rut': '18600010', 'div': '1',
        'nombre': 'Lucas', 'apellido_paterno': 'Espinoza', 'apellido_materno': 'Fuentes',
        'correo': 'lucas.espinozaF@gem.cl', 'telefono': '975000010',
        'direccion': 'Calle Gardenia 150', 'fecha_nacimiento': date(2003, 5, 13),
        'contacto_emergencia': 'Papa: 955000010',
        'curso': cursos[7],
        'password': 'lespinoza'
    },
    {
    'rut': '18600011', 'div': '1',
    'nombre': 'Fernanda', 'apellido_paterno': 'Mendoza', 'apellido_materno': 'Campos',
    'correo': 'fernanda.mendozaC@gem.cl', 'telefono': '975000011',
    'direccion': 'Calle Orquídea 162', 'fecha_nacimiento': date(2003, 2, 7),
    'contacto_emergencia': 'Mama: 955000011',
    'curso': cursos[7],
    'password': 'fmendoza'
    },
    {
        'rut': '18600012', 'div': '2',
        'nombre': 'Javier', 'apellido_paterno': 'Rivas', 'apellido_materno': 'Paredes',
        'correo': 'javier.rivasP@gem.cl', 'telefono': '975000012',
        'direccion': 'Calle Tulipán 174', 'fecha_nacimiento': date(2003, 9, 21),
        'contacto_emergencia': 'Papa: 955000012',
        'curso': cursos[7],
        'password': 'jrivas'
    },
    {
        'rut': '18600013', 'div': '3',
        'nombre': 'Catalina', 'apellido_paterno': 'Sandoval', 'apellido_materno': 'López',
        'correo': 'catalina.sandovalL@gem.cl', 'telefono': '975000013',
        'direccion': 'Calle Margarita 186', 'fecha_nacimiento': date(2003, 12, 30),
        'contacto_emergencia': 'Mama: 955000013',
        'curso': cursos[7],
        'password': 'csandoval'
    },
    {
        'rut': '18600014', 'div': '4',
        'nombre': 'Sebastián', 'apellido_paterno': 'González', 'apellido_materno': 'Rojas',
        'correo': 'sebastian.gonzalezR@gem.cl', 'telefono': '975000014',
        'direccion': 'Calle Lirio 198', 'fecha_nacimiento': date(2003, 6, 1),
        'contacto_emergencia': 'Papa: 955000014',
        'curso': cursos[7],
        'password': 'sgonzalez'
    },
    {
        'rut': '18600015', 'div': '5',
        'nombre': 'Martina', 'apellido_paterno': 'Vega', 'apellido_materno': 'Fuentes',
        'correo': 'martina.vegaF@gem.cl', 'telefono': '975000015',
        'direccion': 'Calle Jazmín 210', 'fecha_nacimiento': date(2003, 3, 18),
        'contacto_emergencia': 'Mama: 955000015',
        'curso': cursos[7],
        'password': 'mvega'
    },
    {
        'rut': '18600016', 'div': '6',
        'nombre': 'Andrés', 'apellido_paterno': 'Contreras', 'apellido_materno': 'Silva',
        'correo': 'andres.contrerasS@gem.cl', 'telefono': '975000016',
        'direccion': 'Calle Gardenia 222', 'fecha_nacimiento': date(2003, 7, 9),
        'contacto_emergencia': 'Papa: 955000016',
        'curso': cursos[7],
        'password': 'acontreras'
    },
    {
        'rut': '18600017', 'div': '6',
        'nombre': 'Paula', 'apellido_paterno': 'Herrera', 'apellido_materno': 'Morales',
        'correo': 'paula.herreraM@gem.cl', 'telefono': '975000017',
        'direccion': 'Calle Orquídea 234', 'fecha_nacimiento': date(2003, 11, 22),
        'contacto_emergencia': 'Mama: 955000017',
        'curso': cursos[7],
        'password': 'pherrera'
    },
    {
        'rut': '18600018', 'div': '6',
        'nombre': 'Ignacio', 'apellido_paterno': 'Pérez', 'apellido_materno': 'Vargas',
        'correo': 'ignacio.perezV@gem.cl', 'telefono': '975000018',
        'direccion': 'Calle Tulipán 246', 'fecha_nacimiento': date(2003, 5, 4),
        'contacto_emergencia': 'Papa: 955000018',
        'curso': cursos[7],
        'password': 'iperezv'
    },
    {
        'rut': '18600019', 'div': '9',
        'nombre': 'Sofía', 'apellido_paterno': 'Salinas', 'apellido_materno': 'Olivares',
        'correo': 'sofia.salinasO@gem.cl', 'telefono': '975000019',
        'direccion': 'Calle Margarita 258', 'fecha_nacimiento': date(2003, 9, 13),
        'contacto_emergencia': 'Mama: 955000019',
        'curso': cursos[7],
        'password': 'ssalinas'
    },
    {
        'rut': '18600020', 'div': '5',
        'nombre': 'Tomás', 'apellido_paterno': 'Ortiz', 'apellido_materno': 'Pinto',
        'correo': 'tomas.ortizP@gem.cl', 'telefono': '975000020',
        'direccion': 'Calle Lirio 270', 'fecha_nacimiento': date(2003, 12, 28),
        'contacto_emergencia': 'Papa: 955000020',
        'curso': cursos[7],
        'password': 'tortiz'
    },
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

print("✅ Estudiantes creados exitosamente")


