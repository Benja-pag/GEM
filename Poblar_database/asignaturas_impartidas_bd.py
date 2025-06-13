import os
import django
from datetime import date
import sys
import unicodedata
# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from Core.models import (
    AuthUser, Usuario, Especialidad, Docente, Administrativo, Curso, Estudiante, EvaluacionBase, Asignatura, AsignaturaImpartida, Clase, HorarioCurso
)

def normalize_string(s):
    # Normaliza (quita tildes) y convierte a minúsculas, eliminando espacios extra
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii').lower().strip()

def verificar_conflictos(dia, horario, sala, docente, curso):
    """
    Verifica si hay conflictos de horario para una clase
    """
    # Verificar si el docente ya tiene clase en ese horario
    clases_docente = Clase.objects.filter(
        asignatura_impartida__docente=docente,
        fecha=dia,
        horario=horario
    )
    if clases_docente.exists():
        return False, f"El docente {docente} ya tiene clase en {dia} horario {horario}"

    # Verificar si la sala está ocupada (solo para salas especiales)
    if sala in ['GIMNASIO', 'LAB_BIO', 'LAB_QUI', 'LAB_FIS', 'SALA_9', 'SALA_10']:
        clases_sala = Clase.objects.filter(
            fecha=dia,
            horario=horario,
            sala=sala
        )
        if clases_sala.exists():
            return False, f"La sala {sala} ya está ocupada en {dia} horario {horario}"

    # Verificar si el curso ya tiene clase
    clases_curso = Clase.objects.filter(
        curso=curso,
        fecha=dia,
        horario=horario
    )
    if clases_curso.exists():
        return False, f"El curso {curso} ya tiene clase en {dia} horario {horario}"

    return True, "No hay conflictos"

def get_sala_por_curso(nivel, letra):
    """
    Asigna una sala fija según el nivel y letra del curso
    """
    return f"SALA_{(nivel-1)*2 + (1 if letra == 'A' else 2)}"

# Datos de asignaturas impartidas con sus horarios
asignaturas_impartidas_data = [
    # 1°A
    ("LEN1A", "Lenguaje", "15345638", 1, "A", [("LUNES", "6"), ("JUEVES", "1")]),
    ("MAT1A", "Matemáticas", "15456786", 1, "A", [("JUEVES", "3"), ("MIERCOLES", "6")]),
    ("HIS1A", "Historia", "16176543", 1, "A", [("MARTES", "3"), ("VIERNES", "6")]),
    ("BIO1A", "Biología", "16376543", 1, "A", [("VIERNES", "2"), ("MIERCOLES", "1")]),
    ("FÍS1A", "Física", "16476543", 1, "A", [("MARTES", "1"), ("MIERCOLES", "5")]),
    ("QUÍ1A", "Química", "17776543", 1, "A", [("MIERCOLES", "4"), ("MARTES", "6")]),
    ("ING1A", "Inglés", "17888888", 1, "A", [("LUNES", "2"), ("MARTES", "4")]),
    ("EDU1A", "Educación Física", "17111111", 1, "A", [("MIERCOLES", "3"), ("LUNES", "1")]),
    ("ART1A", "Arte", "18680246", 1, "A", [("VIERNES", "3"), ("JUEVES", "6")]),
    ("MÚS1A", "Música", "20579136", 1, "A", [("LUNES", "3"), ("MARTES", "5")]),
    ("TEC1A", "Tecnología", "18791357", 1, "A", [("LUNES", "5"), ("VIERNES", "1")]),
    
    # 1°B
    ("LEN1B", "Lenguaje", "15543210", 1, "B", [("LUNES", "1"), ("MIERCOLES", "6")]),
    ("MAT1B", "Matemáticas", "15654321", 1, "B", [("LUNES", "2"), ("JUEVES", "4")]),
    ("HIS1B", "Historia", "16176543", 1, "B", [("VIERNES", "1"), ("MARTES", "4")]),
    ("BIO1B", "Biología", "16376543", 1, "B", [("LUNES", "5"), ("VIERNES", "6")]),
    ("FÍS1B", "Física", "16476543", 1, "B", [("MIERCOLES", "1"), ("MARTES", "1")]),
    ("QUÍ1B", "Química", "17776543", 1, "B", [("MARTES", "6"), ("JUEVES", "2")]),
    ("ING1B", "Inglés", "17888888", 1, "B", [("JUEVES", "1"), ("MIERCOLES", "4")]),
    ("EDU1B", "Educación Física", "17111111", 1, "B", [("MARTES", "3"), ("VIERNES", "3")]),
    ("ART1B", "Arte", "18680246", 1, "B", [("MIERCOLES", "2"), ("JUEVES", "6")]),
    ("MÚS1B", "Música", "20579136", 1, "B", [("LUNES", "6"), ("MIERCOLES", "3")]),
    ("TEC1B", "Tecnología", "18791357", 1, "B", [("JUEVES", "3"), ("VIERNES", "2")]),
    
    # 2°A
    ("LEN2A", "Lenguaje", "15345638", 2, "A", [("LUNES", "1"), ("MIERCOLES", "6")]),
    ("MAT2A", "Matemáticas", "21135792", 2, "A", [("MARTES", "1"), ("JUEVES", "2")]),
    ("HIS2A", "Historia", "16176543", 2, "A", [("VIERNES", "1"), ("MIERCOLES", "2")]),
    ("BIO2A", "Biología", "16376543", 2, "A", [("LUNES", "3"), ("VIERNES", "4")]),
    ("FÍS2A", "Física", "16476543", 2, "A", [("MARTES", "4"), ("MIERCOLES", "1")]),
    ("QUÍ2A", "Química", "20913579", 2, "A", [("JUEVES", "4"), ("VIERNES", "2")]),
    ("ING2A", "Inglés", "17888888", 2, "A", [("MIERCOLES", "4"), ("LUNES", "5")]),
    ("EDU2A", "Educación Física", "17121212", 2, "A", [("MARTES", "3"), ("JUEVES", "6")]),
    ("ART2A", "Arte", "18680246", 2, "A", [("LUNES", "6"), ("VIERNES", "5")]),
    ("MÚS2A", "Música", "20579136", 2, "A", [("MIERCOLES", "3"), ("JUEVES", "1")]),
    ("TEC2A", "Tecnología", "18802468", 2, "A", [("JUEVES", "3"), ("VIERNES", "6")]),
    
    # 2°B
    ("LEN2B", "Lenguaje", "15543210", 2, "B", [("LUNES", "1"), ("MIERCOLES", "6")]),
    ("MAT2B", "Matemáticas", "15654321", 2, "B", [("MARTES", "1"), ("JUEVES", "2")]),
    ("HIS2B", "Historia", "16321098", 2, "B", [("MIERCOLES", "1"), ("VIERNES", "2")]),
    ("BIO2B", "Biología", "20802468", 2, "B", [("LUNES", "2"), ("JUEVES", "4")]),
    ("FÍS2B", "Física", "16576543", 2, "B", [("MARTES", "4"), ("MIERCOLES", "2")]),
    ("QUÍ2B", "Química", "17776543", 2, "B", [("VIERNES", "1"), ("MARTES", "3")]),
    ("ING2B", "Inglés", "17999999", 2, "B", [("MIERCOLES", "4"), ("LUNES", "5")]),
    ("EDU2B", "Educación Física", "17111111", 2, "B", [("JUEVES", "1"), ("VIERNES", "6")]),
    ("ART2B", "Arte", "18579135", 2, "B", [("LUNES", "6"), ("VIERNES", "3")]),
    ("MÚS2B", "Música", "20579136", 2, "B", [("MIERCOLES", "3"), ("JUEVES", "3")]),
    ("TEC2B", "Tecnología", "18791357", 2, "B", [("JUEVES", "6"), ("VIERNES", "5")]),
    
    # 3°A
    ("LEN3A", "Lenguaje", "15432109", 3, "A", [("LUNES", "1"), ("MIERCOLES", "6")]),
    ("MAT3A", "Matemáticas", "15654321", 3, "A", [("MARTES", "1"), ("JUEVES", "2")]),
    ("HIS3A", "Historia", "16321098", 3, "A", [("MIERCOLES", "1"), ("VIERNES", "2")]),
    ("BIO3A", "Biología", "20802468", 3, "A", [("LUNES", "2"), ("JUEVES", "4")]),
    ("FÍS3A", "Física", "16576543", 3, "A", [("MARTES", "4"), ("MIERCOLES", "2")]),
    ("QUÍ3A", "Química", "16676543", 3, "A", [("VIERNES", "1"), ("MARTES", "3")]),
    ("ING3A", "Inglés", "17999999", 3, "A", [("MIERCOLES", "4"), ("LUNES", "5")]),
    ("EDU3A", "Educación Física", "17121212", 3, "A", [("JUEVES", "1"), ("VIERNES", "6")]),
    ("FIL3A", "Filosofía", "18913579", 3, "A", [("LUNES", "6"), ("VIERNES", "3")]),
    
    # 3°B
    ("LEN3B", "Lenguaje", "15432109", 3, "B", [("LUNES", "3"), ("MIERCOLES", "3")]),
    ("MAT3B", "Matemáticas", "15654321", 3, "B", [("MARTES", "2"), ("JUEVES", "3")]),
    ("HIS3B", "Historia", "16321098", 3, "B", [("LUNES", "4"), ("VIERNES", "5")]),
    ("BIO3B", "Biología", "20802468", 3, "B", [("MARTES", "5"), ("MIERCOLES", "5")]),
    ("FÍS3B", "Física", "16576543", 3, "B", [("LUNES", "5"), ("JUEVES", "5")]),
    ("QUÍ3B", "Química", "16676543", 3, "B", [("MARTES", "6"), ("VIERNES", "4")]),
    ("ING3B", "Inglés", "17999999", 3, "B", [("MIERCOLES", "6"), ("JUEVES", "6")]),
    ("EDU3B", "Educación Física", "17121212", 3, "B", [("VIERNES", "1"), ("VIERNES", "6")]),
    ("FIL3B", "Filosofía", "18913579", 3, "B", [("JUEVES", "6"), ("VIERNES", "2")]),
    
    # 4°A
    ("LEN4A", "Lenguaje", "15345638", 4, "A", [("LUNES", "1"), ("MIERCOLES", "2")]),
    ("MAT4A", "Matemáticas", "21135792", 4, "A", [("MARTES", "1"), ("JUEVES", "1")]),
    ("HIS4A", "Historia", "16176543", 4, "A", [("LUNES", "2"), ("VIERNES", "2")]),
    ("BIO4A", "Biología", "16376543", 4, "A", [("MIERCOLES", "1"), ("VIERNES", "3")]),
    ("FIS4A", "Física", "16476543", 4, "A", [("JUEVES", "2"), ("VIERNES", "4")]),
    ("QUI4A", "Química", "17776543", 4, "A", [("MARTES", "2"), ("VIERNES", "5")]),
    ("ING4A", "Inglés", "17888888", 4, "A", [("MIERCOLES", "4"), ("JUEVES", "3")]),
    ("EDU4A", "Educación Física", "17111111", 4, "A", [("MARTES", "3"), ("JUEVES", "4")]),
    ("FIL4A", "Filosofía", "18913579", 4, "A", [("LUNES", "6"), ("VIERNES", "1")]),
    
    # 4°B
    ("LEN4B", "Lenguaje", "15432109", 4, "B", [("LUNES", "1"), ("MIERCOLES", "2")]),
    ("MAT4B", "Matemáticas", "15654321", 4, "B", [("MARTES", "1"), ("JUEVES", "1")]),
    ("HIS4B", "Historia", "16321098", 4, "B", [("LUNES", "2"), ("VIERNES", "2")]),
    ("BIO4B", "Biología", "16276543", 4, "B", [("MIERCOLES", "1"), ("VIERNES", "3")]),
    ("FIS4B", "Física", "16576543", 4, "B", [("JUEVES", "2"), ("VIERNES", "4")]),
    ("QUI4B", "Química", "20913579", 4, "B", [("MARTES", "2"), ("VIERNES", "5")]),
    ("ING4B", "Inglés", "17999999", 4, "B", [("MIERCOLES", "4"), ("JUEVES", "3")]),
    ("EDU4B", "Educación Física", "17121212", 4, "B", [("MARTES", "3"), ("JUEVES", "4")]),
    ("FIL4B", "Filosofía", "18913579", 4, "B", [("LUNES", "6"), ("VIERNES", "1")])
]

# Mapeo de equivalencias entre asignaturas y especialidades
asignatura_especialidad_equivalencias = {
    'Lenguaje': ['Lenguaje', 'Literatura y Escritura Creativa'],
    'Matemáticas': ['Matematicas', 'Matemáticas Discretas', 'Estadística y Análisis de Datos'],
    'Historia': ['Historia', 'Historia del Arte y Cultura', 'Sociología y Estudios Sociales'],
    'Biología': ['Biologia', 'Biología Avanzada', 'Ciencias de la Tierra y Medio Ambiente', 'Educación Ambiental y Sostenibilidad'],
    'Física': ['Fisica', 'Física Aplicada', 'Astronomía y Ciencias del Espacio'],
    'Química': ['Quimica', 'Química Experimental'],
    'Inglés': ['Ingles'],
    'Educación Física': ['Educación Fisica', 'Teatro y Expresión Corporal'],
    'Arte': ['Arte', 'Historia del Arte y Cultura'],
    'Música': ['Música y Composición'],
    'Tecnología': ['Tecnologia', 'Tecnología e Innovación', 'Programación y Robótica'],
    'Filosofía': ['Filosofía y Ética', 'Taller de Debate y Oratoria'],
    'Psicología y Desarrollo Humano': ['Psicología y Desarrollo Humano'],
    'Sociología y Estudios Sociales': ['Sociología y Estudios Sociales'],
    'Física Aplicada': ['Física Aplicada', 'Fisica'],
    'Matemática Avanzada': ['Matemáticas Discretas', 'Matematicas'],
    'Literatura y Escritura Creativa': ['Literatura y Escritura Creativa', 'Lenguaje'],
    'Biología Avanzada': ['Biología Avanzada', 'Biologia'],
    'Química Experimental': ['Química Experimental', 'Quimica']
}

def verificar_especialidad_docente(nombre_asignatura, especialidad_docente):
    """
    Verifica si un docente puede impartir una asignatura basado en su especialidad
    y las equivalencias definidas
    """
    nombre_asignatura = normalize_string(nombre_asignatura)
    especialidad_docente = normalize_string(especialidad_docente)
    
    # Si la especialidad coincide exactamente
    if nombre_asignatura == especialidad_docente:
        return True
        
    # Buscar en las equivalencias
    for asignatura, especialidades in asignatura_especialidad_equivalencias.items():
        if normalize_string(asignatura) == nombre_asignatura:
            return any(normalize_string(esp) == especialidad_docente for esp in especialidades)
    
    return False

def crear_asignaturas_impartidas():
    from Core.models import Especialidad, Asignatura
    # Crear un mapeo rut -> especialidad_nombre
    docentes_especialidad = {}
    for data in [
        {'rut': '15345638', 'especialidad': 'Lenguaje'},
        {'rut': '15456786', 'especialidad': 'Matematicas'},
        {'rut': '15654321', 'especialidad': 'Matematicas'},
        {'rut': '15543210', 'especialidad': 'Lenguaje'},
        {'rut': '15432109', 'especialidad': 'Lenguaje'},
        {'rut': '16321098', 'especialidad': 'Historia'},
        {'rut': '16176543', 'especialidad': 'Historia'},
        {'rut': '16276543', 'especialidad': 'Biologia'},
        {'rut': '16376543', 'especialidad': 'Biologia'},
        {'rut': '16476543', 'especialidad': 'Fisica'},
        {'rut': '16576543', 'especialidad': 'Fisica'},
        {'rut': '16676543', 'especialidad': 'Quimica'},
        {'rut': '17776543', 'especialidad': 'Quimica'},
        {'rut': '17888888', 'especialidad': 'Ingles'},
        {'rut': '17999999', 'especialidad': 'Ingles'},
        {'rut': '17111111', 'especialidad': 'Educación Fisica'},
        {'rut': '17121212', 'especialidad': 'Educación Fisica'},
        {'rut': '18579135', 'especialidad': 'Arte'},
        {'rut': '18680246', 'especialidad': 'Arte'},
        {'rut': '18791357', 'especialidad': 'Tecnologia'},
        {'rut': '18802468', 'especialidad': 'Tecnologia'},
        {'rut': '18913579', 'especialidad': 'Filosofía y Ética'},
        {'rut': '19024680', 'especialidad': 'Literatura y Escritura Creativa'},
        {'rut': '19135791', 'especialidad': 'Historia del Arte y Cultura'},
        {'rut': '19246802', 'especialidad': 'Psicología y Desarrollo Humano'},
        {'rut': '19357913', 'especialidad': 'Sociología y Estudios Sociales'},
        {'rut': '19468024', 'especialidad': 'Teatro y Expresión Corporal'},
        {'rut': '20579136', 'especialidad': 'Música y Composición'},
        {'rut': '20680247', 'especialidad': 'Taller de Debate y Oratoria'},
        {'rut': '20791358', 'especialidad': 'Educación Ambiental y Sostenibilidad'},
        {'rut': '20802468', 'especialidad': 'Biología Avanzada'},
        {'rut': '20913579', 'especialidad': 'Química Experimental'},
        {'rut': '21024680', 'especialidad': 'Física Aplicada'},
        {'rut': '21135792', 'especialidad': 'Matemáticas Discretas'},
        {'rut': '21246803', 'especialidad': 'Programación y Robótica'},
        {'rut': '21357914', 'especialidad': 'Astronomía y Ciencias del Espacio'},
        {'rut': '21246891', 'especialidad': 'Investigación Científica y Método Experimental'},
        {'rut': '14257913', 'especialidad': 'Tecnología e Innovación'},
        {'rut': '13268024', 'especialidad': 'Ciencias de la Tierra y Medio Ambiente'},
        {'rut': '12279135', 'especialidad': 'Estadística y Análisis de Datos'},
        {'rut': '11280246', 'especialidad': 'Estadística y Análisis de Datos'}
    ]:
        docentes_especialidad[data['rut']] = data['especialidad']

    asignaturas_creadas = 0
    for data in asignaturas_impartidas_data:
        try:
            codigo = data[0]
            nombre_asignatura = data[1]
            rut_docente = data[2]
            nivel = data[3]
            letra = data[4]
            horarios = data[5]
            sala = data[6] if len(data) > 6 else get_sala_por_curso(nivel, letra)

            # Verificar especialidad usando el nuevo sistema de equivalencias
            especialidad_docente = docentes_especialidad.get(rut_docente, None)
            if especialidad_docente is None or not verificar_especialidad_docente(nombre_asignatura, especialidad_docente):
                print(f"⛔ Docente {rut_docente} no puede impartir {nombre_asignatura} (especialidad: {especialidad_docente})")
                continue

            # Verificar si la asignatura es electiva
            asignatura_obj = Asignatura.objects.get(nombre=nombre_asignatura, nivel=nivel)
            if getattr(asignatura_obj, 'es_electivo', False):
                print(f"⛔ Asignatura electiva omitida: {nombre_asignatura} ({codigo})")
                continue

            # Filtrar horarios: solo bloques 1 a 6
            horarios_filtrados = [(dia, bloque) for (dia, bloque) in horarios if bloque in ["1","2","3","4","5","6"]]
            if not horarios_filtrados:
                print(f"⛔ No hay bloques válidos (1-6) para {codigo} - {nombre_asignatura}")
                continue

            docente = Docente.objects.get(usuario__rut=rut_docente)
            curso = Curso.objects.get(nivel=nivel, letra=letra)

            asignatura_impartida, created = AsignaturaImpartida.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'asignatura': asignatura_obj,
                    'docente': docente
                }
            )

            clases_creadas = 0
            for dia, horario in horarios_filtrados:
                if dia == "VIERNES" and horario in ["7", "8", "9"]:
                    print(f"⚠️ Horario {horario} no válido para viernes en {codigo}")
                    continue
                sin_conflictos, mensaje = verificar_conflictos(dia, horario, sala, docente, curso)
                if sin_conflictos:
                    clase, created = Clase.objects.get_or_create(
                        asignatura_impartida=asignatura_impartida,
                        curso=curso,
                        fecha=dia,
                        horario=horario,
                        sala=sala
                    )
                    if created:
                        clases_creadas += 1
                else:
                    print(f"⚠️ Conflicto en {codigo}: {mensaje}")
            
            if clases_creadas > 0:
                asignaturas_creadas += 1
                print(f"✅ Creada asignatura {codigo} ({nombre_asignatura}) con {clases_creadas} clases")
            
        except Exception as e:
            print(f"Error al crear asignatura impartida {codigo}: {str(e)}")

    print(f"\n✅ Proceso completado:")
    print(f"- Total de asignaturas impartidas creadas: {asignaturas_creadas}")

if __name__ == "__main__":
    crear_asignaturas_impartidas()

print("✅ Asignaturas impartidas y clases creadas exitosamente")