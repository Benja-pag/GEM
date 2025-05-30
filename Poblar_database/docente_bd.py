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
# Crear especialidades
especialidades_nombres = [
    # 0-30 
    "Ninguna", "Matematicas", "Lenguaje",  "Historia", "Biologia", "Fisica", "Quimica", "Ingles", "Educación Fisica",  "Arte", 
    "Tecnologia", "Filosofía y Ética", "Literatura y Escritura Creativa", "Historia del Arte y Cultura", "Psicología y Desarrollo Humano", "Sociología y Estudios Sociales", 
    "Teatro y Expresión Corporal", "Música y Composición", "Taller de Debate y Oratoria", "Educación Ambiental y Sostenibilidad", #"Derechos Humanos y Ciudadanía", 
    "Biología Avanzada", "Química Experimental", "Física Aplicada", "Matemáticas Discretas", "Programación y Robótica", "Astronomía y Ciencias del Espacio", 
    "Investigación Científica y Método Experimental", "Tecnología e Innovación", "Ciencias de la Tierra y Medio Ambiente", "Estadística y Análisis de Datos" 
]
especialidades = []
for nombre in especialidades_nombres:
    esp, _ = Especialidad.objects.get_or_create(nombre=nombre)
    especialidades.append(esp)

# Crear docentes
docentes_data = [
    {'rut': '15345638', 'div': '9','nombre': 'Juan', 'apellido_paterno': 'Perez', 'apellido_materno': 'Lopez','correo': 'juan.perez@gem.cl', 'telefono': '111111111','direccion': 'Calle Falsa 123', 'fecha_nacimiento': date(1980, 5, 10),'especialidad': especialidades[0], 'password': 'JPerez'},
    {'rut': '15456786', 'div': '5','nombre': 'Maria', 'apellido_paterno': 'Gonzalez', 'apellido_materno': 'Ruiz','correo': 'maria.gonzalez@gem.cl', 'telefono': '222222222','direccion': 'Av. Siempre Viva 742', 'fecha_nacimiento': date(1985, 8, 20),'especialidad': especialidades[1], 'password': 'MGonzalez'},
    {'rut': '15654321', 'div': '2','nombre': 'Pedro', 'apellido_paterno': 'Sanchez', 'apellido_materno': 'Torres','correo': 'pedro.sanchez@gem.cl', 'telefono': '333333333','direccion': 'Calle Uno 111', 'fecha_nacimiento': date(1982, 6, 18),'especialidad': especialidades[1], 'password': 'PSanchez'},
    {'rut': '15543210', 'div': '4','nombre': 'Lucia', 'apellido_paterno': 'Martinez', 'apellido_materno': 'Diaz','correo': 'lucia.martinez@gem.cl', 'telefono': '444444444','direccion': 'Calle Dos 222', 'fecha_nacimiento': date(1987, 9, 30),'especialidad': especialidades[2], 'password': 'LMartinez'},
    {'rut': '15432109', 'div': '6','nombre': 'Javier', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Fuentes','correo': 'javier.rojas@gem.cl', 'telefono': '555555555','direccion': 'Calle Tres 333', 'fecha_nacimiento': date(1983, 2, 11),'especialidad': especialidades[2], 'password': 'JRojas'},
    {'rut': '16321098', 'div': '8','nombre': 'Carmen', 'apellido_paterno': 'Vidal', 'apellido_materno': 'Carrasco','correo': 'carmen.vidal@gem.cl', 'telefono': '666666666','direccion': 'Calle Cuatro 444', 'fecha_nacimiento': date(1984, 12, 3),'especialidad': especialidades[3], 'password': 'CVidal'},
    {'rut': '16176543','div': '1','nombre': 'Isabel', 'apellido_paterno': 'Fernandez', 'apellido_materno': 'Salazar','correo': 'isabel.fernandez@gem.cl', 'telefono': '121212121','direccion': 'Calle Nueve 999', 'fecha_nacimiento': date(1988, 6, 12),'especialidad': especialidades[3], 'password': 'IFernandez'},
    {'rut': '16276543', 'div': '2','nombre': 'Tomas', 'apellido_paterno': 'Herrera', 'apellido_materno': 'Bravo','correo': 'tomas.herrera@gem.cl', 'telefono': '131313131','direccion': 'Calle Diez 1010', 'fecha_nacimiento': date(1981, 1, 8),'especialidad': especialidades[4], 'password': 'THerrera'},
    {'rut': '16376543', 'div': '3','nombre': 'Daniela', 'apellido_paterno': 'Reyes', 'apellido_materno': 'Munoz','correo': 'daniela.reyes@gem.cl', 'telefono': '141414141','direccion': 'Calle Once 1111', 'fecha_nacimiento': date(1990, 10, 14),'especialidad': especialidades[4], 'password': 'DReyes'},
    {'rut': '16476543', 'div': '4','nombre': 'Matias', 'apellido_paterno': 'Lagos', 'apellido_materno': 'Zamora','correo': 'matias.lagos@gem.cl', 'telefono': '151515151','direccion': 'Calle Doce 1212', 'fecha_nacimiento': date(1985, 5, 5),'especialidad': especialidades[5], 'password': 'MLagos'},
    {'rut': '16576543', 'div': '5','nombre': 'Fernanda', 'apellido_paterno': 'Castro', 'apellido_materno': 'Ahumada','correo': 'fernanda.castro@gem.cl', 'telefono': '161616161','direccion': 'Calle Trece 1313', 'fecha_nacimiento': date(1986, 8, 19),'especialidad': especialidades[5], 'password': 'FCastro'},
    {'rut': '16676543', 'div': '6','nombre': 'Sebastian', 'apellido_paterno': 'Gutierrez', 'apellido_materno': 'Ovalle','correo': 'sebastian.gutierrez@gem.cl', 'telefono': '171717171','direccion': 'Calle Catorce 1414', 'fecha_nacimiento': date(1983, 2, 2),'especialidad': especialidades[6], 'password': 'SGutierrez'},
    {'rut': '17776543', 'div': '7','nombre': 'Rocio', 'apellido_paterno': 'Alvarado', 'apellido_materno': 'Contreras','correo': 'rocio.alvarado@gem.cl', 'telefono': '181818181','direccion': 'Calle Quince 1515', 'fecha_nacimiento': date(1987, 7, 7),'especialidad': especialidades[6], 'password': 'RAlvarado'},
    {'rut': '17888888', 'div': '8','nombre': 'Cristobal', 'apellido_paterno': 'Navarro', 'apellido_materno': 'Morales','correo': 'cristobal.navarro@gem.cl', 'telefono': '191919191','direccion': 'Calle Dieciseis 1616', 'fecha_nacimiento': date(1980, 4, 22),'especialidad': especialidades[7], 'password': 'CNavarro'},
    {'rut': '17999999', 'div': '9','nombre': 'Valentina', 'apellido_paterno': 'Saavedra', 'apellido_materno': 'Leon','correo': 'valentina.saavedra@gem.cl', 'telefono': '202020202','direccion': 'Calle Diecisiete 1717', 'fecha_nacimiento': date(1991, 3, 17),'especialidad': especialidades[7], 'password': 'VSaavedra'},
    {'rut': '17111111', 'div': '1','nombre': 'Felipe', 'apellido_paterno': 'Ortega', 'apellido_materno': 'Riquelme','correo': 'felipe.ortega@gem.cl', 'telefono': '212121212','direccion': 'Calle Dieciocho 1818', 'fecha_nacimiento': date(1989, 11, 11),'especialidad': especialidades[8], 'password': 'FOrtega'},
    {'rut': '17121212', 'div': '2','nombre': 'Antonia', 'apellido_paterno': 'Silva', 'apellido_materno': 'Paredes','correo': 'antonia.silva@gem.cl', 'telefono': '222222222','direccion': 'Calle Diecinueve 1919', 'fecha_nacimiento': date(1982, 12, 24),'especialidad': especialidades[8], 'password': 'ASilva'},
    {'rut': '18579135', 'div': '1','nombre': 'Angela', 'apellido_paterno': 'Dias', 'apellido_materno': 'Araya','correo': 'angela.dias@gem.cl', 'telefono': '232323232','direccion': 'Calle Veinte 2020', 'fecha_nacimiento': date(1981, 1, 15),'especialidad': especialidades[9], 'password': 'ADias'},
    {'rut': '18680246', 'div': '2','nombre': 'Carlos', 'apellido_paterno': 'Ibarra', 'apellido_materno': 'Gallardo','correo': 'carlos.ibarra@gem.cl', 'telefono': '242424242','direccion': 'Calle Veintiuno 2121', 'fecha_nacimiento': date(1979, 6, 9),'especialidad': especialidades[9], 'password': 'CIbarra'},
    {'rut': '18791357', 'div': '3','nombre': 'Beatriz', 'apellido_paterno': 'Leiva', 'apellido_materno': 'Vergara','correo': 'beatriz.leiva@gem.cl', 'telefono': '252525252','direccion': 'Calle Veintidós 2222', 'fecha_nacimiento': date(1986, 3, 28),'especialidad': especialidades[10], 'password': 'BLeiva'},
    {'rut': '18802468', 'div': '4','nombre': 'Gonzalo', 'apellido_paterno': 'Meza', 'apellido_materno': 'Toro','correo': 'gonzalo.meza@gem.cl', 'telefono': '262626262','direccion': 'Calle Veintitrés 2323', 'fecha_nacimiento': date(1982, 10, 2),'especialidad': especialidades[10], 'password': 'GMeza'},
    {'rut': '18913579', 'div': '5','nombre': 'Paula', 'apellido_paterno': 'Escobar', 'apellido_materno': 'Campos','correo': 'paula.escobar@gem.cl', 'telefono': '272727272','direccion': 'Calle Veinticuatro 2424', 'fecha_nacimiento': date(1987, 7, 13),'especialidad': especialidades[11], 'password': 'PEscobar'},
    {'rut': '19024680', 'div': '6','nombre': 'Ricardo', 'apellido_paterno': 'Alarcon', 'apellido_materno': 'Delgado','correo': 'ricardo.alarcon@gem.cl', 'telefono': '282828282','direccion': 'Calle Veinticinco 2525', 'fecha_nacimiento': date(1980, 12, 5),'especialidad': especialidades[12], 'password': 'RAlarcon'},
    {'rut': '19135791', 'div': '7','nombre': 'Camila', 'apellido_paterno': 'Farias', 'apellido_materno': 'Montenegro','correo': 'camila.farias@gem.cl', 'telefono': '292929292','direccion': 'Calle Veintiséis 2626', 'fecha_nacimiento': date(1990, 9, 18),'especialidad': especialidades[13], 'password': 'CFarias'},
    {'rut': '19246802', 'div': '8','nombre': 'Esteban', 'apellido_paterno': 'Morales', 'apellido_materno': 'Venegas','correo': 'esteban.morales@gem.cl', 'telefono': '303030303','direccion': 'Calle Veintisiete 2727', 'fecha_nacimiento': date(1983, 4, 20),'especialidad': especialidades[14], 'password': 'EMorales'},
    {'rut': '19357913', 'div': '9','nombre': 'Francisca', 'apellido_paterno': 'Bustos', 'apellido_materno': 'Rebolledo','correo': 'francisca.bustos@gem.cl', 'telefono': '313131313','direccion': 'Calle Veintiocho 2828', 'fecha_nacimiento': date(1984, 8, 8),'especialidad': especialidades[15], 'password': 'FBustos'},
    {'rut': '19468024', 'div': '1','nombre': 'Ignacio', 'apellido_paterno': 'Pizarro', 'apellido_materno': 'Acuña','correo': 'ignacio.pizarro@gem.cl', 'telefono': '323232323','direccion': 'Calle Veintinueve 2929', 'fecha_nacimiento': date(1981, 2, 25),'especialidad': especialidades[16], 'password': 'IPizarro'},
    {'rut': '20579136', 'div': '2','nombre': 'Lorena', 'apellido_paterno': 'Valdes', 'apellido_materno': 'Cornejo','correo': 'lorena.valdes@gem.cl', 'telefono': '333333333','direccion': 'Calle Treinta 3030', 'fecha_nacimiento': date(1986, 6, 16),'especialidad': especialidades[17], 'password': 'LValdes'},
    {'rut': '20680247', 'div': '3','nombre': 'Mauricio', 'apellido_paterno': 'Peña', 'apellido_materno': 'Cifuentes','correo': 'mauricio.pena@gem.cl', 'telefono': '343434343','direccion': 'Calle Treinta y Uno 3131', 'fecha_nacimiento': date(1980, 3, 3),'especialidad': especialidades[18], 'password': 'MPena'},
    {'rut': '20791358', 'div': '4','nombre': 'Barbara', 'apellido_paterno': 'Soto', 'apellido_materno': 'Gallardo','correo': 'barbara.soto@gem.cl', 'telefono': '353535353','direccion': 'Calle Treinta y Dos 3232', 'fecha_nacimiento': date(1992, 1, 14),'especialidad': especialidades[19], 'password': 'BSoto'},
    {'rut': '20802468', 'div': '5','nombre': 'Rodrigo', 'apellido_paterno': 'Castillo', 'apellido_materno': 'Yanez','correo': 'rodrigo.castillo@gem.cl', 'telefono': '363636363','direccion': 'Calle Treinta y Tres 3333', 'fecha_nacimiento': date(1987, 11, 5),'especialidad': especialidades[20], 'password': 'RCastillo'},
    {'rut': '20913579', 'div': '6','nombre': 'Daniela', 'apellido_paterno': 'Alvarez', 'apellido_materno': 'Espinoza','correo': 'daniela.alvarez@gem.cl', 'telefono': '373737373','direccion': 'Calle Treinta y Cuatro 3434', 'fecha_nacimiento': date(1989, 10, 23),'especialidad': especialidades[21], 'password': 'DAlvarez'},
    {'rut': '21024680', 'div': '7','nombre': 'Victor', 'apellido_paterno': 'Carrillo', 'apellido_materno': 'Barrientos','correo': 'victor.carrillo@gem.cl', 'telefono': '383838383','direccion': 'Calle Treinta y Cinco 3535', 'fecha_nacimiento': date(1981, 12, 2),'especialidad': especialidades[22], 'password': 'VCarrillo'},
    {'rut': '21135792', 'div': '8','nombre': 'Alejandra', 'apellido_paterno': 'Mendez', 'apellido_materno': 'Rojas','correo': 'alejandra.mendez@gem.cl', 'telefono': '393939393','direccion': 'Calle Treinta y Seis 3636', 'fecha_nacimiento': date(1990, 4, 27),'especialidad': especialidades[23], 'password': 'AMendez'},
    {'rut': '21246803', 'div': '9','nombre': 'Gabriel', 'apellido_paterno': 'Saez', 'apellido_materno': 'Figueroa','correo': 'gabriel.saez@gem.cl', 'telefono': '404040404','direccion': 'Calle Treinta y Siete 3737', 'fecha_nacimiento': date(1986, 7, 9),'especialidad': especialidades[24], 'password': 'GSaez'},
    {'rut': '21357914', 'div': '1','nombre': 'Camila', 'apellido_paterno': 'Fuenzalida', 'apellido_materno': 'Naranjo','correo': 'camila.fuenzalida@gem.cl', 'telefono': '414141414','direccion': 'Calle Treinta y Ocho 3838', 'fecha_nacimiento': date(1993, 3, 16),'especialidad': especialidades[25], 'password': 'CFuenzalida'},
    {'rut': '21246891', 'div': '2','nombre': 'Diego', 'apellido_paterno': 'Zambrano', 'apellido_materno': 'Cornejo','correo': 'diego.zambrano@gem.cl', 'telefono': '424242424','direccion': 'Calle Treinta y Nueve 3939', 'fecha_nacimiento': date(1984, 6, 11),'especialidad': especialidades[26], 'password': 'DZambrano'},
    {'rut': '14257913', 'div': '3','nombre': 'Natalia', 'apellido_paterno': 'Baeza', 'apellido_materno': 'Ortega','correo': 'natalia.baeza@gem.cl', 'telefono': '434343434','direccion': 'Calle Cuarenta 4040', 'fecha_nacimiento': date(1988, 9, 28),'especialidad': especialidades[27], 'password': 'NBaeza'},
    {'rut': '13268024', 'div': '4','nombre': 'Esteban', 'apellido_paterno': 'Cuevas', 'apellido_materno': 'Gallardo','correo': 'esteban.cuevas@gem.cl', 'telefono': '444444444','direccion': 'Calle Cuarenta y Uno 4141', 'fecha_nacimiento': date(1981, 8, 6),'especialidad': especialidades[28], 'password': 'ECuevas'},
    {'rut': '12279135', 'div': '5','nombre': 'Paula', 'apellido_paterno': 'Vergara', 'apellido_materno': 'Mora','correo': 'paula.vergara@gem.cl', 'telefono': '454545454','direccion': 'Calle Cuarenta y Dos 4242', 'fecha_nacimiento': date(1992, 5, 1),'especialidad': especialidades[29], 'password': 'PVergara'},
    {'rut': '11280246', 'div': '6','nombre': 'Cristian', 'apellido_paterno': 'Ojeda', 'apellido_materno': 'Venegas','correo': 'cristian.ojeda@gem.cl', 'telefono': '464646464','direccion': 'Calle Cuarenta y Tres 4343', 'fecha_nacimiento': date(1985, 12, 20),'especialidad': especialidades[29], 'password': 'COjeda'}
]

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
    Docente.objects.get_or_create(
        usuario=usuario,
        defaults={'especialidad': data['especialidad']}
    )

print("✅ Docentes creados exitosamente")

