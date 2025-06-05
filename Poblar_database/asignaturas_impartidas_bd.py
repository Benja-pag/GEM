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
    AuthUser, Usuario, Especialidad, Docente, Administrativo, Curso, Estudiante, EvaluacionBase, Asignatura, AsignaturaImpartida, Clase, HorarioCurso
)

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

# Datos de asignaturas impartidas y sus clases
asignaturas_impartidas_data = [
    # 1° Medio A
    ("LEN1A", "Lenguaje", "15345638", 1, "A", [("LUNES", "1"), ("MIERCOLES", "2")]),
    ("MAT1A", "Matemáticas", "15456786", 1, "A", [("MARTES", "1"), ("JUEVES", "2")]),
    ("HIS1A", "Historia", "15654321", 1, "A", [("LUNES", "3"), ("VIERNES", "4")]),
    ("BIO1A", "Biología", "15543210", 1, "A", [("LUNES", "5"), ("MIERCOLES", "4")]),
    ("FIS1A", "Física", "15432109", 1, "A", [("MARTES", "3"), ("JUEVES", "4")]),
    ("QUI1A", "Química", "16321098", 1, "A", [("LUNES", "7"), ("VIERNES", "2")]),
    
    # 1° Medio B
    ("LEN1B", "Lenguaje", "15345638", 1, "B", [("LUNES", "2"), ("MIERCOLES", "1")]),
    ("MAT1B", "Matemáticas", "15456786", 1, "B", [("MARTES", "2"), ("JUEVES", "1")]),
    ("HIS1B", "Historia", "15654321", 1, "B", [("LUNES", "4"), ("VIERNES", "3")]),
    ("BIO1B", "Biología", "15543210", 1, "B", [("LUNES", "6"), ("MIERCOLES", "3")]),
    ("FIS1B", "Física", "15432109", 1, "B", [("MARTES", "4"), ("JUEVES", "3")]),
    ("QUI1B", "Química", "16321098", 1, "B", [("LUNES", "8"), ("VIERNES", "1")]),

    # 2° Medio A
    ("LEN2A", "Lenguaje", "16676543", 2, "A", [("LUNES", "1"), ("MIERCOLES", "2")]),
    ("MAT2A", "Matemáticas", "17776543", 2, "A", [("MARTES", "1"), ("JUEVES", "2")]),
    ("HIS2A", "Historia", "17888888", 2, "A", [("LUNES", "3"), ("VIERNES", "4")]),
    ("BIO2A", "Biología", "17999999", 2, "A", [("LUNES", "5"), ("MIERCOLES", "4")]),
    ("FIS2A", "Física", "17111111", 2, "A", [("MARTES", "3"), ("JUEVES", "4")]),
    ("QUI2A", "Química", "17121212", 2, "A", [("LUNES", "7"), ("VIERNES", "2")]),
    ("ING2A", "Inglés", "18579135", 2, "A", [("MARTES", "5"), ("JUEVES", "6")]),
    ("EFI2A", "Educación Física", "18680246", 2, "A", [("MIERCOLES", "5"), ("VIERNES", "1")], "GIMNASIO"),
    ("ART2A", "Arte", "18791357", 2, "A", [("MARTES", "7"), ("JUEVES", "5")], "SALA_9"),
    ("MUS2A", "Música", "18802468", 2, "A", [("MIERCOLES", "6"), ("VIERNES", "3")], "SALA_9"),
    ("TEC2A", "Tecnología", "18913579", 2, "A", [("LUNES", "6"), ("MIERCOLES", "7")], "SALA_9"),

    # 2° Medio B
    ("LEN2B", "Lenguaje", "16676543", 2, "B", [("LUNES", "2"), ("MIERCOLES", "1")]),
    ("MAT2B", "Matemáticas", "17776543", 2, "B", [("MARTES", "2"), ("JUEVES", "1")]),
    ("HIS2B", "Historia", "17888888", 2, "B", [("LUNES", "4"), ("VIERNES", "3")]),
    ("BIO2B", "Biología", "17999999", 2, "B", [("LUNES", "6"), ("MIERCOLES", "3")]),
    ("FIS2B", "Física", "17111111", 2, "B", [("MARTES", "4"), ("JUEVES", "3")]),
    ("QUI2B", "Química", "17121212", 2, "B", [("LUNES", "8"), ("VIERNES", "1")]),
    ("ING2B", "Inglés", "18579135", 2, "B", [("MARTES", "6"), ("JUEVES", "7")]),
    ("EFI2B", "Educación Física", "18680246", 2, "B", [("MIERCOLES", "7"), ("VIERNES", "2")], "GIMNASIO"),
    ("ART2B", "Arte", "18791357", 2, "B", [("MARTES", "8"), ("JUEVES", "6")], "SALA_10"),
    ("MUS2B", "Música", "18802468", 2, "B", [("MIERCOLES", "8"), ("VIERNES", "5")], "SALA_10"),
    ("TEC2B", "Tecnología", "18913579", 2, "B", [("LUNES", "5"), ("MIERCOLES", "6")], "SALA_10"),

    # 3° Medio A
    ("LEN3A", "Lenguaje", "19024680", 3, "A", [("LUNES", "1"), ("MIERCOLES", "2")]),
    ("MAT3A", "Matemáticas", "19135791", 3, "A", [("MARTES", "1"), ("JUEVES", "2")]),
    ("HIS3A", "Historia", "15345638", 3, "A", [("LUNES", "3"), ("VIERNES", "4")]),
    ("BIO3A", "Biología", "15456786", 3, "A", [("LUNES", "5"), ("MIERCOLES", "4")]),
    ("FIS3A", "Física", "15654321", 3, "A", [("MARTES", "3"), ("JUEVES", "4")]),
    ("QUI3A", "Química", "15543210", 3, "A", [("LUNES", "7"), ("VIERNES", "2")]),
    ("ING3A", "Inglés", "15432109", 3, "A", [("MARTES", "5"), ("JUEVES", "6")]),
    ("EFI3A", "Educación Física", "16321098", 3, "A", [("MIERCOLES", "5"), ("VIERNES", "1")], "GIMNASIO"),
    ("FIL3A", "Filosofía", "16176543", 3, "A", [("MARTES", "7"), ("JUEVES", "5")]),

    # 3° Medio B
    ("LEN3B", "Lenguaje", "19024680", 3, "B", [("LUNES", "2"), ("MIERCOLES", "1")]),
    ("MAT3B", "Matemáticas", "19135791", 3, "B", [("MARTES", "2"), ("JUEVES", "1")]),
    ("HIS3B", "Historia", "15345638", 3, "B", [("LUNES", "4"), ("VIERNES", "3")]),
    ("BIO3B", "Biología", "15456786", 3, "B", [("LUNES", "6"), ("MIERCOLES", "3")]),
    ("FIS3B", "Física", "15654321", 3, "B", [("MARTES", "4"), ("JUEVES", "3")]),
    ("QUI3B", "Química", "15543210", 3, "B", [("LUNES", "8"), ("VIERNES", "1")]),
    ("ING3B", "Inglés", "15432109", 3, "B", [("MARTES", "6"), ("JUEVES", "7")]),
    ("EFI3B", "Educación Física", "16321098", 3, "B", [("MIERCOLES", "7"), ("VIERNES", "2")], "GIMNASIO"),
    ("FIL3B", "Filosofía", "16176543", 3, "B", [("MARTES", "8"), ("JUEVES", "6")]),

    # 4° Medio A
    ("LEN4A", "Lenguaje", "16276543", 4, "A", [("LUNES", "1"), ("MIERCOLES", "2")]),
    ("MAT4A", "Matemáticas", "16376543", 4, "A", [("MARTES", "1"), ("JUEVES", "2")]),
    ("HIS4A", "Historia", "16476543", 4, "A", [("LUNES", "3"), ("VIERNES", "4")]),
    ("BIO4A", "Biología", "16576543", 4, "A", [("LUNES", "5"), ("MIERCOLES", "4")]),
    ("FIS4A", "Física", "16676543", 4, "A", [("MARTES", "3"), ("JUEVES", "4")]),
    ("QUI4A", "Química", "17776543", 4, "A", [("LUNES", "7"), ("VIERNES", "2")]),
    ("ING4A", "Inglés", "17888888", 4, "A", [("MARTES", "5"), ("JUEVES", "6")]),
    ("EFI4A", "Educación Física", "17999999", 4, "A", [("MIERCOLES", "5"), ("VIERNES", "1")], "GIMNASIO"),
    ("FIL4A", "Filosofía", "17111111", 4, "A", [("MARTES", "7"), ("JUEVES", "5")]),

    # 4° Medio B
    ("LEN4B", "Lenguaje", "16276543", 4, "B", [("LUNES", "2"), ("MIERCOLES", "1")]),
    ("MAT4B", "Matemáticas", "16376543", 4, "B", [("MARTES", "2"), ("JUEVES", "1")]),
    ("HIS4B", "Historia", "16476543", 4, "B", [("LUNES", "4"), ("VIERNES", "3")]),
    ("BIO4B", "Biología", "16576543", 4, "B", [("LUNES", "6"), ("MIERCOLES", "3")]),
    ("FIS4B", "Física", "16676543", 4, "B", [("MARTES", "4"), ("JUEVES", "3")]),
    ("QUI4B", "Química", "17776543", 4, "B", [("LUNES", "8"), ("VIERNES", "1")]),
    ("ING4B", "Inglés", "17888888", 4, "B", [("MARTES", "6"), ("JUEVES", "7")]),
    ("EFI4B", "Educación Física", "17999999", 4, "B", [("MIERCOLES", "7"), ("VIERNES", "2")], "GIMNASIO"),
    ("FIL4B", "Filosofía", "17111111", 4, "B", [("MARTES", "8"), ("JUEVES", "6")]),

    # Electivos 3° Medio (usando salas numéricas y laboratorios)
    ("FIL-E3", "Filosofía y Ética", "17121212", 3, "A", [("MARTES", "6"), ("JUEVES", "7")], "SALA_9"),
    ("LIT-E3", "Literatura y Escritura Creativa", "18579135", 3, "A", [("LUNES", "6"), ("MIERCOLES", "7")], "SALA_9"),
    ("BIO-E3", "Biología Avanzada", "18680246", 3, "A", [("MARTES", "7"), ("JUEVES", "8")], "LAB_BIO"),
    ("QUI-E3", "Química Experimental", "18791357", 3, "A", [("LUNES", "8"), ("MIERCOLES", "8")], "LAB_QUI"),

    # Electivos 4° Medio (usando salas numéricas y laboratorios)
    ("PSI-E4", "Psicología y Desarrollo Humano", "18802468", 4, "A", [("MARTES", "6"), ("JUEVES", "7")], "SALA_10"),
    ("SOC-E4", "Sociología y Estudios Sociales", "18913579", 4, "A", [("LUNES", "6"), ("MIERCOLES", "7")], "SALA_10"),
    ("FIS-E4", "Física Aplicada", "19024680", 4, "A", [("MARTES", "7"), ("JUEVES", "8")], "LAB_FIS"),
    ("MAT-E4", "Matemática Avanzada", "19135791", 4, "A", [("LUNES", "8"), ("MIERCOLES", "8")], "SALA_10")
]

def crear_asignaturas_impartidas():
    # Crear asignaturas impartidas y sus clases
    for data in asignaturas_impartidas_data:
        try:
            codigo = data[0]
            nombre_asignatura = data[1]
            rut_docente = data[2]
            nivel = data[3]
            letra = data[4]
            horarios = data[5]
            # La sala puede ser especificada o se asigna según el curso
            sala = data[6] if len(data) > 6 else get_sala_por_curso(nivel, letra)
            
            # Obtener la asignatura y el docente
            asignatura = Asignatura.objects.get(nombre=nombre_asignatura, nivel=nivel)
            docente = Docente.objects.get(usuario__rut=rut_docente)
            curso = Curso.objects.get(nivel=nivel, letra=letra)
            
            # Crear la asignatura impartida
            asignatura_impartida, created = AsignaturaImpartida.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'asignatura': asignatura,
                    'docente': docente
                }
            )
            
            # Crear las clases para esta asignatura impartida
            for dia, horario in horarios:
                # Verificar si el horario es válido para el día
                if dia == "VIERNES" and horario in ["7", "8", "9"]:
                    print(f"⚠️ Horario {horario} no válido para viernes en {codigo}")
                    continue
                    
                # Verificar conflictos
                sin_conflictos, mensaje = verificar_conflictos(dia, horario, sala, docente, curso)
                if sin_conflictos:
                    Clase.objects.get_or_create(
                        asignatura_impartida=asignatura_impartida,
                        curso=curso,
                        fecha=dia,
                        horario=horario,
                        sala=sala
                    )
                else:
                    print(f"⚠️ Conflicto en {codigo}: {mensaje}")
                    
        except Exception as e:
            print(f"Error al crear asignatura impartida {codigo}: {str(e)}")

if __name__ == "__main__":
    crear_asignaturas_impartidas()

print("✅ Asignaturas impartidas y clases creadas exitosamente")