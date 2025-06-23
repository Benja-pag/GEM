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
    AuthUser, Usuario, Especialidad, Docente, Administrativo, Curso, Estudiante, EvaluacionBase, Asignatura, AsignaturaImpartida,
    ProfesorJefe
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
    {'rut': '15345638', 'div': '9','nombre': 'Juan', 'apellido_paterno': 'Perez', 'apellido_materno': 'Lopez','correo': 'juan.perez@gem.cl', 'telefono': '111111111','direccion': 'Calle Falsa 123', 'fecha_nacimiento': date(1980, 5, 10),'especialidad': especialidades[2], 'password': 'JPerez', 'es_profesor_jefe': True},
    {'rut': '15456786', 'div': '5','nombre': 'Maria', 'apellido_paterno': 'Gonzalez', 'apellido_materno': 'Ruiz','correo': 'maria.gonzalez@gem.cl', 'telefono': '222222222','direccion': 'Av. Siempre Viva 742', 'fecha_nacimiento': date(1985, 8, 20),'especialidad': especialidades[1], 'password': 'MGonzalez', 'es_profesor_jefe': True},
    {'rut': '15654321', 'div': '2','nombre': 'Pedro', 'apellido_paterno': 'Sanchez', 'apellido_materno': 'Torres','correo': 'pedro.sanchez@gem.cl', 'telefono': '333333333','direccion': 'Calle Uno 111', 'fecha_nacimiento': date(1982, 6, 18),'especialidad': especialidades[1], 'password': 'PSanchez', 'es_profesor_jefe': True},
    {'rut': '15543210', 'div': '4','nombre': 'Lucia', 'apellido_paterno': 'Martinez', 'apellido_materno': 'Diaz','correo': 'lucia.martinez@gem.cl', 'telefono': '444444444','direccion': 'Calle Dos 222', 'fecha_nacimiento': date(1987, 9, 30),'especialidad': especialidades[2], 'password': 'LMartinez', 'es_profesor_jefe': True},
    {'rut': '15432109', 'div': '6','nombre': 'Javier', 'apellido_paterno': 'Rojas', 'apellido_materno': 'Fuentes','correo': 'javier.rojas@gem.cl', 'telefono': '555555555','direccion': 'Calle Tres 333', 'fecha_nacimiento': date(1983, 2, 11),'especialidad': especialidades[2], 'password': 'JRojas', 'es_profesor_jefe': True},
    {'rut': '16321098', 'div': '8','nombre': 'Carmen', 'apellido_paterno': 'Vidal', 'apellido_materno': 'Carrasco','correo': 'carmen.vidal@gem.cl', 'telefono': '666666666','direccion': 'Calle Cuatro 444', 'fecha_nacimiento': date(1984, 12, 3),'especialidad': especialidades[3], 'password': 'CVidal', 'es_profesor_jefe': True},
    {'rut': '16176543','div': '1','nombre': 'Isabel', 'apellido_paterno': 'Fernandez', 'apellido_materno': 'Salazar','correo': 'isabel.fernandez@gem.cl', 'telefono': '121212121','direccion': 'Calle Nueve 999', 'fecha_nacimiento': date(1988, 6, 12),'especialidad': especialidades[3], 'password': 'IFernandez', 'es_profesor_jefe': True},
    {'rut': '16276543', 'div': '2','nombre': 'Tomas', 'apellido_paterno': 'Herrera', 'apellido_materno': 'Bravo','correo': 'tomas.herrera@gem.cl', 'telefono': '131313131','direccion': 'Calle Diez 1010', 'fecha_nacimiento': date(1981, 1, 8),'especialidad': especialidades[4], 'password': 'THerrera', 'es_profesor_jefe': True},
    {'rut': '16376543', 'div': '3','nombre': 'Daniela', 'apellido_paterno': 'Reyes', 'apellido_materno': 'Munoz','correo': 'daniela.reyes@gem.cl', 'telefono': '141414141','direccion': 'Calle Once 1111', 'fecha_nacimiento': date(1990, 10, 14),'especialidad': especialidades[4], 'password': 'DReyes', 'es_profesor_jefe': False},
    {'rut': '16476543', 'div': '4','nombre': 'Matias', 'apellido_paterno': 'Lagos', 'apellido_materno': 'Zamora','correo': 'matias.lagos@gem.cl', 'telefono': '151515151','direccion': 'Calle Doce 1212', 'fecha_nacimiento': date(1985, 5, 5),'especialidad': especialidades[5], 'password': 'MLagos', 'es_profesor_jefe': False},
    {'rut': '16576543', 'div': '5','nombre': 'Fernanda', 'apellido_paterno': 'Castro', 'apellido_materno': 'Ahumada','correo': 'fernanda.castro@gem.cl', 'telefono': '161616161','direccion': 'Calle Trece 1313', 'fecha_nacimiento': date(1986, 8, 19),'especialidad': especialidades[5], 'password': 'FCastro', 'es_profesor_jefe': False},
    {'rut': '16676543', 'div': '6','nombre': 'Sebastian', 'apellido_paterno': 'Gutierrez', 'apellido_materno': 'Ovalle','correo': 'sebastian.gutierrez@gem.cl', 'telefono': '171717171','direccion': 'Calle Catorce 1414', 'fecha_nacimiento': date(1983, 2, 2),'especialidad': especialidades[6], 'password': 'SGutierrez', 'es_profesor_jefe': False},
    {'rut': '17776543', 'div': '7','nombre': 'Rocio', 'apellido_paterno': 'Alvarado', 'apellido_materno': 'Contreras','correo': 'rocio.alvarado@gem.cl', 'telefono': '181818181','direccion': 'Calle Quince 1515', 'fecha_nacimiento': date(1987, 7, 7),'especialidad': especialidades[6], 'password': 'RAlvarado', 'es_profesor_jefe': False},
    {'rut': '17888888', 'div': '8','nombre': 'Cristobal', 'apellido_paterno': 'Navarro', 'apellido_materno': 'Morales','correo': 'cristobal.navarro@gem.cl', 'telefono': '191919191','direccion': 'Calle Dieciseis 1616', 'fecha_nacimiento': date(1980, 4, 22),'especialidad': especialidades[7], 'password': 'CNavarro', 'es_profesor_jefe': False},
    {'rut': '17999999', 'div': '9','nombre': 'Valentina', 'apellido_paterno': 'Saavedra', 'apellido_materno': 'Leon','correo': 'valentina.saavedra@gem.cl', 'telefono': '202020202','direccion': 'Calle Diecisiete 1717', 'fecha_nacimiento': date(1991, 3, 17),'especialidad': especialidades[7], 'password': 'VSaavedra', 'es_profesor_jefe': False},
    {'rut': '17111111', 'div': '1','nombre': 'Felipe', 'apellido_paterno': 'Ortega', 'apellido_materno': 'Riquelme','correo': 'felipe.ortega@gem.cl', 'telefono': '212121212','direccion': 'Calle Dieciocho 1818', 'fecha_nacimiento': date(1989, 11, 11),'especialidad': especialidades[8], 'password': 'FOrtega', 'es_profesor_jefe': False},
    {'rut': '17121212', 'div': '2','nombre': 'Antonia', 'apellido_paterno': 'Silva', 'apellido_materno': 'Paredes','correo': 'antonia.silva@gem.cl', 'telefono': '222222222','direccion': 'Calle Diecinueve 1919', 'fecha_nacimiento': date(1982, 12, 24),'especialidad': especialidades[8], 'password': 'ASilva', 'es_profesor_jefe': False},
    {'rut': '18579135', 'div': '1','nombre': 'Angela', 'apellido_paterno': 'Dias', 'apellido_materno': 'Araya','correo': 'angela.dias@gem.cl', 'telefono': '232323232','direccion': 'Calle Veinte 2020', 'fecha_nacimiento': date(1981, 1, 15),'especialidad': especialidades[9], 'password': 'ADias', 'es_profesor_jefe': False},
    {'rut': '18680246', 'div': '2','nombre': 'Carlos', 'apellido_paterno': 'Ibarra', 'apellido_materno': 'Gallardo','correo': 'carlos.ibarra@gem.cl', 'telefono': '242424242','direccion': 'Calle Veintiuno 2121', 'fecha_nacimiento': date(1979, 6, 9),'especialidad': especialidades[9], 'password': 'CIbarra', 'es_profesor_jefe': False},
    {'rut': '18791357', 'div': '3','nombre': 'Beatriz', 'apellido_paterno': 'Leiva', 'apellido_materno': 'Vergara','correo': 'beatriz.leiva@gem.cl', 'telefono': '252525252','direccion': 'Calle Veintidós 2222', 'fecha_nacimiento': date(1986, 3, 28),'especialidad': especialidades[10], 'password': 'BLeiva', 'es_profesor_jefe': False},
    {'rut': '18802468', 'div': '4','nombre': 'Gonzalo', 'apellido_paterno': 'Meza', 'apellido_materno': 'Toro','correo': 'gonzalo.meza@gem.cl', 'telefono': '262626262','direccion': 'Calle Veintitrés 2323', 'fecha_nacimiento': date(1982, 10, 2),'especialidad': especialidades[10], 'password': 'GMeza', 'es_profesor_jefe': False},
    {'rut': '18913579', 'div': '5','nombre': 'Paula', 'apellido_paterno': 'Escobar', 'apellido_materno': 'Campos','correo': 'paula.escobar@gem.cl', 'telefono': '272727272','direccion': 'Calle Veinticuatro 2424', 'fecha_nacimiento': date(1987, 7, 13),'especialidad': especialidades[11], 'password': 'PEscobar', 'es_profesor_jefe': False},
    {'rut': '19024680', 'div': '6','nombre': 'Ricardo', 'apellido_paterno': 'Alarcon', 'apellido_materno': 'Delgado','correo': 'ricardo.alarcon@gem.cl', 'telefono': '282828282','direccion': 'Calle Veinticinco 2525', 'fecha_nacimiento': date(1980, 12, 5),'especialidad': especialidades[12], 'password': 'RAlarcon', 'es_profesor_jefe': False},
    {'rut': '19135791', 'div': '7','nombre': 'Camila', 'apellido_paterno': 'Farias', 'apellido_materno': 'Montenegro','correo': 'camila.farias@gem.cl', 'telefono': '292929292','direccion': 'Calle Veintiséis 2626', 'fecha_nacimiento': date(1990, 9, 18),'especialidad': especialidades[13], 'password': 'CFarias', 'es_profesor_jefe': False},
    {'rut': '19246802', 'div': '8','nombre': 'Esteban', 'apellido_paterno': 'Morales', 'apellido_materno': 'Venegas','correo': 'esteban.morales@gem.cl', 'telefono': '303030303','direccion': 'Calle Veintisiete 2727', 'fecha_nacimiento': date(1983, 4, 20),'especialidad': especialidades[14], 'password': 'EMorales', 'es_profesor_jefe': False},
    {'rut': '19357913', 'div': '9','nombre': 'Francisca', 'apellido_paterno': 'Bustos', 'apellido_materno': 'Rebolledo','correo': 'francisca.bustos@gem.cl', 'telefono': '313131313','direccion': 'Calle Veintiocho 2828', 'fecha_nacimiento': date(1984, 8, 8),'especialidad': especialidades[15], 'password': 'FBustos', 'es_profesor_jefe': False},
    {'rut': '19468024', 'div': '1','nombre': 'Ignacio', 'apellido_paterno': 'Pizarro', 'apellido_materno': 'Acuña','correo': 'ignacio.pizarro@gem.cl', 'telefono': '323232323','direccion': 'Calle Veintinueve 2929', 'fecha_nacimiento': date(1981, 2, 25),'especialidad': especialidades[16], 'password': 'IPizarro', 'es_profesor_jefe': False},
    {'rut': '20579136', 'div': '2','nombre': 'Lorena', 'apellido_paterno': 'Valdes', 'apellido_materno': 'Cornejo','correo': 'lorena.valdes@gem.cl', 'telefono': '333333333','direccion': 'Calle Treinta 3030', 'fecha_nacimiento': date(1986, 6, 16),'especialidad': especialidades[17], 'password': 'LValdes', 'es_profesor_jefe': False},
    {'rut': '20680247', 'div': '3','nombre': 'Mauricio', 'apellido_paterno': 'Peña', 'apellido_materno': 'Cifuentes','correo': 'mauricio.pena@gem.cl', 'telefono': '343434343','direccion': 'Calle Treinta y Uno 3131', 'fecha_nacimiento': date(1980, 3, 3),'especialidad': especialidades[18], 'password': 'MPena', 'es_profesor_jefe': False},
    {'rut': '20791358', 'div': '4','nombre': 'Barbara', 'apellido_paterno': 'Soto', 'apellido_materno': 'Gallardo','correo': 'barbara.soto@gem.cl', 'telefono': '353535353','direccion': 'Calle Treinta y Dos 3232', 'fecha_nacimiento': date(1992, 1, 14),'especialidad': especialidades[19], 'password': 'BSoto', 'es_profesor_jefe': False},
    {'rut': '20802468', 'div': '5','nombre': 'Rodrigo', 'apellido_paterno': 'Castillo', 'apellido_materno': 'Yanez','correo': 'rodrigo.castillo@gem.cl', 'telefono': '363636363','direccion': 'Calle Treinta y Tres 3333', 'fecha_nacimiento': date(1987, 11, 5),'especialidad': especialidades[20], 'password': 'RCastillo', 'es_profesor_jefe': False},
    {'rut': '20913579', 'div': '6','nombre': 'Daniela', 'apellido_paterno': 'Alvarez', 'apellido_materno': 'Espinoza','correo': 'daniela.alvarez@gem.cl', 'telefono': '373737373','direccion': 'Calle Treinta y Cuatro 3434', 'fecha_nacimiento': date(1989, 10, 23),'especialidad': especialidades[21], 'password': 'DAlvarez', 'es_profesor_jefe': False},
    {'rut': '21024680', 'div': '7','nombre': 'Victor', 'apellido_paterno': 'Carrillo', 'apellido_materno': 'Barrientos','correo': 'victor.carrillo@gem.cl', 'telefono': '383838383','direccion': 'Calle Treinta y Cinco 3535', 'fecha_nacimiento': date(1981, 12, 2),'especialidad': especialidades[22], 'password': 'VCarrillo', 'es_profesor_jefe': False},
    {'rut': '21135792', 'div': '8','nombre': 'Alejandra', 'apellido_paterno': 'Mendez', 'apellido_materno': 'Rojas','correo': 'alejandra.mendez@gem.cl', 'telefono': '393939393','direccion': 'Calle Treinta y Seis 3636', 'fecha_nacimiento': date(1990, 4, 27),'especialidad': especialidades[23], 'password': 'AMendez', 'es_profesor_jefe': False},
    {'rut': '21246803', 'div': '9','nombre': 'Gabriel', 'apellido_paterno': 'Saez', 'apellido_materno': 'Figueroa','correo': 'gabriel.saez@gem.cl', 'telefono': '404040404','direccion': 'Calle Treinta y Siete 3737', 'fecha_nacimiento': date(1986, 7, 9),'especialidad': especialidades[24], 'password': 'GSaez', 'es_profesor_jefe': False},
    {'rut': '21357914', 'div': '1','nombre': 'Camila', 'apellido_paterno': 'Fuenzalida', 'apellido_materno': 'Naranjo','correo': 'camila.fuenzalida@gem.cl', 'telefono': '414141414','direccion': 'Calle Treinta y Ocho 3838', 'fecha_nacimiento': date(1993, 3, 16),'especialidad': especialidades[25], 'password': 'CFuenzalida', 'es_profesor_jefe': False},
    {'rut': '21246891', 'div': '2','nombre': 'Diego', 'apellido_paterno': 'Zambrano', 'apellido_materno': 'Cornejo','correo': 'diego.zambrano@gem.cl', 'telefono': '424242424','direccion': 'Calle Treinta y Nueve 3939', 'fecha_nacimiento': date(1984, 6, 11),'especialidad': especialidades[26], 'password': 'DZambrano', 'es_profesor_jefe': False},
    {'rut': '14257913', 'div': '3','nombre': 'Natalia', 'apellido_paterno': 'Baeza', 'apellido_materno': 'Ortega','correo': 'natalia.baeza@gem.cl', 'telefono': '434343434','direccion': 'Calle Cuarenta 4040', 'fecha_nacimiento': date(1988, 9, 28),'especialidad': especialidades[27], 'password': 'NBaeza', 'es_profesor_jefe': False},
    {'rut': '13268024', 'div': '4','nombre': 'Esteban', 'apellido_paterno': 'Cuevas', 'apellido_materno': 'Gallardo','correo': 'esteban.cuevas@gem.cl', 'telefono': '444444444','direccion': 'Calle Cuarenta y Uno 4141', 'fecha_nacimiento': date(1981, 8, 6),'especialidad': especialidades[28], 'password': 'ECuevas', 'es_profesor_jefe': False},
    {'rut': '12279135', 'div': '5','nombre': 'Paula', 'apellido_paterno': 'Vergara', 'apellido_materno': 'Mora','correo': 'paula.vergara@gem.cl', 'telefono': '454545454','direccion': 'Calle Cuarenta y Dos 4242', 'fecha_nacimiento': date(1992, 5, 1),'especialidad': especialidades[29], 'password': 'PVergara', 'es_profesor_jefe': False},
    {'rut': '11280246', 'div': '6','nombre': 'Cristian', 'apellido_paterno': 'Ojeda', 'apellido_materno': 'Venegas','correo': 'cristian.ojeda@gem.cl', 'telefono': '464646464','direccion': 'Calle Cuarenta y Tres 4343', 'fecha_nacimiento': date(1985, 12, 20),'especialidad': especialidades[29], 'password': 'COjeda', 'es_profesor_jefe': False},
    
    # --- 8 Nuevos Docentes para Electivos ---
    {'rut': '10101010', 'div': '1','nombre': 'Roberto', 'apellido_paterno': 'Gomez', 'apellido_materno': 'Bolaños','correo': 'roberto.gomez@gem.cl', 'telefono': '505050505','direccion': 'Vecindad 8', 'fecha_nacimiento': date(1980, 1, 1),'especialidad': especialidades[24], 'password': 'RGomez', 'es_profesor_jefe': False}, # Programación y Robótica
    {'rut': '10202020', 'div': '2','nombre': 'Florinda', 'apellido_paterno': 'Meza', 'apellido_materno': 'García','correo': 'florinda.meza@gem.cl', 'telefono': '515151515','direccion': 'Calle Jupiter 12', 'fecha_nacimiento': date(1981, 2, 2),'especialidad': especialidades[16], 'password': 'FMeza', 'es_profesor_jefe': False}, # Teatro y Expresión Corporal
    {'rut': '10303030', 'div': '3','nombre': 'Ruben', 'apellido_paterno': 'Aguirre', 'apellido_materno': 'Fuentes','correo': 'ruben.aguirre@gem.cl', 'telefono': '525252525','direccion': 'Escuela de Profesores 1', 'fecha_nacimiento': date(1979, 3, 3),'especialidad': especialidades[18], 'password': 'RAguirre', 'es_profesor_jefe': False}, # Taller de Debate y Oratoria
    {'rut': '10404040', 'div': '4','nombre': 'Edgar', 'apellido_paterno': 'Vivar', 'apellido_materno': 'Villanueva','correo': 'edgar.vivar@gem.cl', 'telefono': '535353535','direccion': 'Calle Barriga 45', 'fecha_nacimiento': date(1978, 4, 4),'especialidad': especialidades[13], 'password': 'EVivar', 'es_profesor_jefe': False}, # Historia del Arte y Cultura
    {'rut': '10505050', 'div': '5','nombre': 'Angelines', 'apellido_paterno': 'Fernandez', 'apellido_materno': 'Abad','correo': 'angelines.fernandez@gem.cl', 'telefono': '545454545','direccion': 'Depto 71', 'fecha_nacimiento': date(1975, 5, 5),'especialidad': especialidades[29], 'password': 'AFernandez', 'es_profesor_jefe': False}, # Estadística y Análisis de Datos
    {'rut': '10606060', 'div': '6','nombre': 'Ramon', 'apellido_paterno': 'Valdes', 'apellido_materno': 'Castillo','correo': 'ramon.valdes@gem.cl', 'telefono': '555555555','direccion': 'Calle Renta 14', 'fecha_nacimiento': date(1976, 6, 6),'especialidad': especialidades[25], 'password': 'RValdes', 'es_profesor_jefe': False}, # Astronomía y Ciencias del Espacio
    {'rut': '10707070', 'div': '7','nombre': 'Carlos', 'apellido_paterno': 'Villagran', 'apellido_materno': 'Eslava','correo': 'carlos.villagran@gem.cl', 'telefono': '565656565','direccion': 'Cachetes 22', 'fecha_nacimiento': date(1982, 7, 7),'especialidad': especialidades[26], 'password': 'CVillagran', 'es_profesor_jefe': False}, # Investigación Científica
    {'rut': '10808080', 'div': '8','nombre': 'Maria', 'apellido_paterno': 'Antonieta', 'apellido_materno': 'de las Nieves','correo': 'maria.antonieta@gem.cl', 'telefono': '575757575','direccion': 'Pelluhue 30', 'fecha_nacimiento': date(1983, 8, 8),'especialidad': especialidades[19], 'password': 'MAntonieta', 'es_profesor_jefe': False} # Educación Ambiental
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
    docente, created = Docente.objects.get_or_create(
        usuario=usuario,
        defaults={
            'especialidad': data['especialidad'],
            'es_profesor_jefe': data['es_profesor_jefe']
        }
    )
    
    # Si el docente ya existía, actualizamos el campo es_profesor_jefe
    if not created:
        docente.es_profesor_jefe = data['es_profesor_jefe']
        docente.save()

print("✅ Docentes creados exitosamente")

# Asignar profesores jefe a los cursos
profesores_jefe_data = [
    # (rut_docente, nivel_curso, letra_curso)
    ("15345638", 1, "A"),  # Juan Perez - 1°A
    ("15456786", 1, "B"),  # Maria Gonzalez - 1°B
    ("15654321", 2, "A"),  # Pedro Sanchez - 2°A
    ("15543210", 2, "B"),  # Lucia Martinez - 2°B
    ("15432109", 3, "A"),  # Javier Rojas - 3°A
    ("16321098", 3, "B"),  # Carmen Vidal - 3°B
    ("16176543", 4, "A"),  # Isabel Fernandez - 4°A
    ("16276543", 4, "B"),  # Tomas Herrera - 4°B
]

# Crear las asignaciones de profesor jefe
for rut_docente, nivel, letra in profesores_jefe_data:
    try:
        docente = Docente.objects.get(usuario__rut=rut_docente)
        curso = Curso.objects.get(nivel=nivel, letra=letra)
        
        # Verificar si ya existe una jefatura para este curso
        ProfesorJefe.objects.filter(curso=curso).delete()
        
        # Crear la nueva jefatura
        ProfesorJefe.objects.create(
            docente=docente,
            curso=curso
        )
        print(f"✅ Profesor jefe asignado: {docente.usuario.nombre} {docente.usuario.apellido_paterno} - {curso}")
        
    except Docente.DoesNotExist:
        print(f"⚠️ No se encontró el docente con RUT: {rut_docente}")
    except Curso.DoesNotExist:
        print(f"⚠️ No se encontró el curso: {nivel}°{letra}")
    except Exception as e:
        print(f"⚠️ Error al asignar profesor jefe: {str(e)}")

print("✅ Asignación de profesores jefe completada")

