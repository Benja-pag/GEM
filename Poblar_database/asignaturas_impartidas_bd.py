import os
import django
import sys
from datetime import date
from itertools import product

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import (
    Clase, AsignaturaImpartida, Curso, Docente, Asignatura, Especialidad
)

def obtener_docentes_por_especialidad():
    """Obtiene un diccionario con los docentes agrupados por especialidad"""
    docentes_especialidad = {}
    
    for docente in Docente.objects.select_related('especialidad', 'usuario').all():
        especialidad = docente.especialidad.nombre
        if especialidad not in docentes_especialidad:
            docentes_especialidad[especialidad] = []
        docentes_especialidad[especialidad].append(docente)
    
    return docentes_especialidad

def verificar_especialidad_docente(nombre_asignatura, especialidad_docente):
    """Verifica si un docente puede impartir una asignatura según su especialidad"""
    equivalencias = {
        # Especialidades principales
        "Matematicas": ["Matemáticas", "Matemática Avanzada", "Matemáticas Discretas", "Estadística y Análisis de Datos"],
        "Matemáticas Discretas": ["Matemáticas", "Matemática Avanzada", "Matemáticas Discretas", "Estadística y Análisis de Datos"],
        "Estadística y Análisis de Datos": ["Matemáticas", "Matemática Avanzada", "Matemáticas Discretas", "Estadística y Análisis de Datos"],
        
        "Lenguaje": ["Lenguaje", "Literatura y Escritura Creativa"],
        "Literatura y Escritura Creativa": ["Lenguaje", "Literatura y Escritura Creativa"],
        
        "Historia": ["Historia", "Historia del Arte y Cultura", "Sociología y Estudios Sociales"],
        "Historia del Arte y Cultura": ["Historia", "Historia del Arte y Cultura", "Sociología y Estudios Sociales"],
        "Sociología y Estudios Sociales": ["Historia", "Historia del Arte y Cultura", "Sociología y Estudios Sociales"],
        
        "Biologia": ["Biología", "Biología Avanzada", "Ciencias de la Tierra y Medio Ambiente"],
        "Biología Avanzada": ["Biología", "Biología Avanzada", "Ciencias de la Tierra y Medio Ambiente"],
        "Ciencias de la Tierra y Medio Ambiente": ["Biología", "Biología Avanzada", "Ciencias de la Tierra y Medio Ambiente"],
        
        "Fisica": ["Física", "Física Aplicada", "Astronomía y Ciencias del Espacio"],
        "Física Aplicada": ["Física", "Física Aplicada", "Astronomía y Ciencias del Espacio"],
        "Astronomía y Ciencias del Espacio": ["Física", "Física Aplicada", "Astronomía y Ciencias del Espacio"],
        
        "Quimica": ["Química", "Química Experimental"],
        "Química Experimental": ["Química", "Química Experimental"],
        
        "Ingles": ["Inglés"],
        
        "Educación Fisica": ["Educación Física"],
        
        "Arte": ["Arte", "Historia del Arte y Cultura", "Teatro y Expresión Corporal"],
        "Historia del Arte y Cultura": ["Arte", "Historia del Arte y Cultura", "Teatro y Expresión Corporal"],
        "Teatro y Expresión Corporal": ["Arte", "Historia del Arte y Cultura", "Teatro y Expresión Corporal"],
        
        "Tecnologia": ["Tecnología", "Tecnología e Innovación", "Programación y Robótica"],
        "Tecnología e Innovación": ["Tecnología", "Tecnología e Innovación", "Programación y Robótica"],
        "Programación y Robótica": ["Tecnología", "Tecnología e Innovación", "Programación y Robótica"],
        
        "Filosofía y Ética": ["Filosofía", "Filosofía y Ética"],
        
        "Psicología y Desarrollo Humano": ["Psicología y Desarrollo Humano"],
        
        "Música y Composición": ["Música"],
        
        "Investigación Científica y Método Experimental": ["Biología Avanzada", "Química Experimental", "Física Aplicada"],
    }
    
    if especialidad_docente in equivalencias:
        return nombre_asignatura in equivalencias[especialidad_docente]
    
    return False

def get_sala_por_curso(nivel, letra):
    """Asigna una sala específica según el curso"""
    salas_por_curso = {
        (1, "A"): "SALA_1",
        (1, "B"): "SALA_2", 
        (2, "A"): "SALA_3",
        (2, "B"): "SALA_4",
        (3, "A"): "SALA_5",
        (3, "B"): "SALA_6",
        (4, "A"): "SALA_7",
        (4, "B"): "SALA_8",
    }
    return salas_por_curso.get((nivel, letra), "SALA_1")

def get_sala_especial(asignatura):
    """Asigna salas especiales según la asignatura"""
    salas_especiales = {
        "Educación Física": "GIMNASIO",
        "Biología": "LAB_CIEN",
        "Química": "LAB_CIEN", 
        "Física": "LAB_CIEN",
        "Tecnología": "LAB_COMP",
        "Música": "SALA_9",
        "Arte": "SALA_10"
    }
    return salas_especiales.get(asignatura, None)

def verificar_conflictos_bloques_consecutivos(dia, bloque_inicio, docente, curso, sala):
    """
    Verifica conflictos para bloques consecutivos (2 bloques seguidos)
    Retorna (sin_conflictos, mensaje)
    """
    # Verificar que el bloque siguiente existe
    bloque_siguiente = str(int(bloque_inicio) + 1)
    
    # Si es viernes, solo hasta bloque 6
    if dia == "VIERNES" and int(bloque_inicio) >= 6:
        return False, f"Bloque {bloque_inicio} no válido para viernes"
    
    # Verificar conflictos para ambos bloques
    for bloque in [bloque_inicio, bloque_siguiente]:
    # Verificar si el docente ya tiene clase en ese horario
        if Clase.objects.filter(
        asignatura_impartida__docente=docente,
        fecha=dia,
            horario=bloque
        ).exists():
            return False, f"Docente ya tiene clase en {dia} bloque {bloque}"
        
        # Verificar si el curso ya tiene clase en ese horario
        if Clase.objects.filter(
            curso=curso,
            fecha=dia,
            horario=bloque
        ).exists():
            return False, f"Curso ya tiene clase en {dia} bloque {bloque}"
        
        # Verificar si la sala está ocupada (solo para salas especiales)
        if sala in ['GIMNASIO', 'LAB_BIO', 'LAB_QUI', 'LAB_FIS', 'SALA_9', 'SALA_10', 'LAB_COMP', 'LAB_CIEN']:
            if Clase.objects.filter(
        fecha=dia,
                horario=bloque,
                sala=sala
            ).exists():
                return False, f"Sala {sala} ocupada en {dia} bloque {bloque}"
    
    return True, "Sin conflictos"

def obtener_horarios_disponibles_bloques_consecutivos(docente, curso, sala):
    """
    Obtiene horarios disponibles para bloques consecutivos
    """
    dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
    horarios_disponibles = []
    
    for dia in dias:
        # Para viernes solo hasta bloque 5 (para que quepa el 6)
        max_bloque = 5 if dia == 'VIERNES' else 8
        
        for bloque_inicio in range(1, max_bloque + 1):
            sin_conflictos, _ = verificar_conflictos_bloques_consecutivos(
                dia, str(bloque_inicio), docente, curso, sala
            )
            if sin_conflictos:
                horarios_disponibles.append((dia, str(bloque_inicio)))
    
    return horarios_disponibles

# Datos de asignaturas impartidas con horarios de bloques consecutivos
# Formato: (codigo, nombre_asignatura, rut_docente, nivel, letra, [horarios_consecutivos])
asignaturas_impartidas_data = [
    # 1°A - Bloques consecutivos (1-2, 3-4, 5-6)
    ("LEN1A", "Lenguaje", "15345638", 1, "A", [("LUNES", "1"), ("MIERCOLES", "3")]),
    ("MAT1A", "Matemáticas", "15456786", 1, "A", [("MARTES", "1"), ("JUEVES", "3")]),
    ("HIS1A", "Historia", "16176543", 1, "A", [("LUNES", "5"), ("MIERCOLES", "1")]),
    ("BIO1A", "Biología", "16376543", 1, "A", [("MARTES", "3"), ("JUEVES", "1")]),
    ("FÍS1A", "Física", "16476543", 1, "A", [("LUNES", "3"), ("MIERCOLES", "5")]),
    ("QUÍ1A", "Química", "17776543", 1, "A", [("MARTES", "5"), ("JUEVES", "5")]),
    ("ING1A", "Inglés", "17888888", 1, "A", [("LUNES", "7"), ("MIERCOLES", "7")]),
    ("EDU1A", "Educación Física", "17111111", 1, "A", [("MARTES", "7"), ("JUEVES", "7")]),
    ("ART1A", "Arte", "18680246", 1, "A", [("LUNES", "9"), ("MIERCOLES", "9")]),
    ("MÚS1A", "Música", "20579136", 1, "A", [("MARTES", "9"), ("JUEVES", "9")]),
    ("TEC1A", "Tecnología", "18791357", 1, "A", [("LUNES", "11"), ("MIERCOLES", "11")]),
    
    # 1°B
    ("LEN1B", "Lenguaje", "15543210", 1, "B", [("MARTES", "1"), ("JUEVES", "3")]),
    ("MAT1B", "Matemáticas", "15654321", 1, "B", [("LUNES", "1"), ("MIERCOLES", "3")]),
    ("HIS1B", "Historia", "16176543", 1, "B", [("LUNES", "5"), ("MIERCOLES", "1")]),
    ("BIO1B", "Biología", "16376543", 1, "B", [("MARTES", "3"), ("JUEVES", "1")]),
    ("FÍS1B", "Física", "16476543", 1, "B", [("LUNES", "3"), ("MIERCOLES", "5")]),
    ("QUÍ1B", "Química", "17776543", 1, "B", [("MARTES", "5"), ("JUEVES", "5")]),
    ("ING1B", "Inglés", "17888888", 1, "B", [("LUNES", "7"), ("MIERCOLES", "7")]),
    ("EDU1B", "Educación Física", "17111111", 1, "B", [("MARTES", "7"), ("JUEVES", "7")]),
    ("ART1B", "Arte", "18680246", 1, "B", [("LUNES", "9"), ("MIERCOLES", "9")]),
    ("MÚS1B", "Música", "20579136", 1, "B", [("MARTES", "9"), ("JUEVES", "9")]),
    ("TEC1B", "Tecnología", "18791357", 1, "B", [("LUNES", "11"), ("MIERCOLES", "11")]),
    
    # 2°A
    ("LEN2A", "Lenguaje", "15345638", 2, "A", [("MARTES", "1"), ("JUEVES", "3")]),
    ("MAT2A", "Matemáticas", "21135792", 2, "A", [("LUNES", "1"), ("MIERCOLES", "3")]),
    ("HIS2A", "Historia", "16176543", 2, "A", [("LUNES", "5"), ("MIERCOLES", "1")]),
    ("BIO2A", "Biología", "16376543", 2, "A", [("MARTES", "3"), ("JUEVES", "1")]),
    ("FÍS2A", "Física", "16476543", 2, "A", [("LUNES", "3"), ("MIERCOLES", "5")]),
    ("QUÍ2A", "Química", "20913579", 2, "A", [("MARTES", "5"), ("JUEVES", "5")]),
    ("ING2A", "Inglés", "17888888", 2, "A", [("LUNES", "7"), ("MIERCOLES", "7")]),
    ("EDU2A", "Educación Física", "17121212", 2, "A", [("MARTES", "7"), ("JUEVES", "7")]),
    ("ART2A", "Arte", "18680246", 2, "A", [("LUNES", "9"), ("MIERCOLES", "9")]),
    ("MÚS2A", "Música", "20579136", 2, "A", [("MARTES", "9"), ("JUEVES", "9")]),
    ("TEC2A", "Tecnología", "18802468", 2, "A", [("LUNES", "11"), ("MIERCOLES", "11")]),
    
    # 2°B
    ("LEN2B", "Lenguaje", "15543210", 2, "B", [("LUNES", "1"), ("MIERCOLES", "3")]),
    ("MAT2B", "Matemáticas", "15654321", 2, "B", [("MARTES", "1"), ("JUEVES", "3")]),
    ("HIS2B", "Historia", "16321098", 2, "B", [("LUNES", "5"), ("MIERCOLES", "1")]),
    ("BIO2B", "Biología", "20802468", 2, "B", [("MARTES", "3"), ("JUEVES", "1")]),
    ("FÍS2B", "Física", "16576543", 2, "B", [("LUNES", "3"), ("MIERCOLES", "5")]),
    ("QUÍ2B", "Química", "17776543", 2, "B", [("MARTES", "5"), ("JUEVES", "5")]),
    ("ING2B", "Inglés", "17999999", 2, "B", [("LUNES", "7"), ("MIERCOLES", "7")]),
    ("EDU2B", "Educación Física", "17111111", 2, "B", [("MARTES", "7"), ("JUEVES", "7")]),
    ("ART2B", "Arte", "18579135", 2, "B", [("LUNES", "9"), ("MIERCOLES", "9")]),
    ("MÚS2B", "Música", "20579136", 2, "B", [("MARTES", "9"), ("JUEVES", "9")]),
    ("TEC2B", "Tecnología", "18791357", 2, "B", [("LUNES", "11"), ("MIERCOLES", "11")]),
    
    # 3°A
    ("LEN3A", "Lenguaje", "15432109", 3, "A", [("MARTES", "1"), ("JUEVES", "3")]),
    ("MAT3A", "Matemáticas", "15654321", 3, "A", [("LUNES", "1"), ("MIERCOLES", "3")]),
    ("HIS3A", "Historia", "16321098", 3, "A", [("LUNES", "5"), ("MIERCOLES", "1")]),
    ("BIO3A", "Biología", "20802468", 3, "A", [("MARTES", "3"), ("JUEVES", "1")]),
    ("FÍS3A", "Física", "16576543", 3, "A", [("LUNES", "3"), ("MIERCOLES", "5")]),
    ("QUÍ3A", "Química", "16676543", 3, "A", [("MARTES", "5"), ("JUEVES", "5")]),
    ("ING3A", "Inglés", "17999999", 3, "A", [("LUNES", "7"), ("MIERCOLES", "7")]),
    ("EDU3A", "Educación Física", "17121212", 3, "A", [("MARTES", "7"), ("JUEVES", "7")]),
    ("FIL3A", "Filosofía", "18913579", 3, "A", [("LUNES", "9"), ("MIERCOLES", "9")]),
    
    # 3°B
    ("LEN3B", "Lenguaje", "15432109", 3, "B", [("LUNES", "1"), ("MIERCOLES", "3")]),
    ("MAT3B", "Matemáticas", "15654321", 3, "B", [("MARTES", "1"), ("JUEVES", "3")]),
    ("HIS3B", "Historia", "16321098", 3, "B", [("LUNES", "5"), ("MIERCOLES", "1")]),
    ("BIO3B", "Biología", "20802468", 3, "B", [("MARTES", "3"), ("JUEVES", "1")]),
    ("FÍS3B", "Física", "16576543", 3, "B", [("LUNES", "3"), ("MIERCOLES", "5")]),
    ("QUÍ3B", "Química", "16676543", 3, "B", [("MARTES", "5"), ("JUEVES", "5")]),
    ("ING3B", "Inglés", "17999999", 3, "B", [("LUNES", "7"), ("MIERCOLES", "7")]),
    ("EDU3B", "Educación Física", "17121212", 3, "B", [("MARTES", "7"), ("JUEVES", "7")]),
    ("FIL3B", "Filosofía", "18913579", 3, "B", [("LUNES", "9"), ("MIERCOLES", "9")]),
    
    # 4°A
    ("LEN4A", "Lenguaje", "15345638", 4, "A", [("MARTES", "1"), ("JUEVES", "3")]),
    ("MAT4A", "Matemáticas", "21135792", 4, "A", [("LUNES", "1"), ("MIERCOLES", "3")]),
    ("HIS4A", "Historia", "16176543", 4, "A", [("LUNES", "5"), ("MIERCOLES", "1")]),
    ("BIO4A", "Biología", "16376543", 4, "A", [("MARTES", "3"), ("JUEVES", "1")]),
    ("FIS4A", "Física", "16476543", 4, "A", [("LUNES", "3"), ("MIERCOLES", "5")]),
    ("QUI4A", "Química", "17776543", 4, "A", [("MARTES", "5"), ("JUEVES", "5")]),
    ("ING4A", "Inglés", "17888888", 4, "A", [("LUNES", "7"), ("MIERCOLES", "7")]),
    ("EDU4A", "Educación Física", "17111111", 4, "A", [("MARTES", "7"), ("JUEVES", "7")]),
    ("FIL4A", "Filosofía", "18913579", 4, "A", [("LUNES", "9"), ("MIERCOLES", "9")]),
    
    # 4°B
    ("LEN4B", "Lenguaje", "15432109", 4, "B", [("LUNES", "1"), ("MIERCOLES", "3")]),
    ("MAT4B", "Matemáticas", "15654321", 4, "B", [("MARTES", "1"), ("JUEVES", "3")]),
    ("HIS4B", "Historia", "16321098", 4, "B", [("LUNES", "5"), ("MIERCOLES", "1")]),
    ("BIO4B", "Biología", "16276543", 4, "B", [("MARTES", "3"), ("JUEVES", "1")]),
    ("FIS4B", "Física", "16576543", 4, "B", [("LUNES", "3"), ("MIERCOLES", "5")]),
    ("QUI4B", "Química", "20913579", 4, "B", [("MARTES", "5"), ("JUEVES", "5")]),
    ("ING4B", "Inglés", "17999999", 4, "B", [("LUNES", "7"), ("MIERCOLES", "7")]),
    ("EDU4B", "Educación Física", "17121212", 4, "B", [("MARTES", "7"), ("JUEVES", "7")]),
    ("FIL4B", "Filosofía", "18913579", 4, "B", [("LUNES", "9"), ("MIERCOLES", "9")])
]

def crear_asignaturas_impartidas():
    """Crea las asignaturas impartidas con horarios de bloques consecutivos"""
    
    # Obtener docentes por especialidad
    docentes_especialidad = obtener_docentes_por_especialidad()
    
    # Limpiar asignaturas impartidas existentes
    AsignaturaImpartida.objects.all().delete()
    Clase.objects.all().delete()

    asignaturas_creadas = 0
    conflictos_resueltos = 0
    
    print("🔄 Creando asignaturas impartidas con bloques consecutivos...")
    
    for data in asignaturas_impartidas_data:
        try:
            codigo = data[0]
            nombre_asignatura = data[1]
            rut_docente = data[2]
            nivel = data[3]
            letra = data[4]
            horarios_originales = data[5]
            
            # Verificar que la asignatura no sea electiva
            asignatura_obj = Asignatura.objects.get(nombre=nombre_asignatura, nivel=nivel)
            if getattr(asignatura_obj, 'es_electivo', False):
                print(f"⛔ Asignatura electiva omitida: {nombre_asignatura} ({codigo})")
                continue

            # Verificar especialidad del docente
            docente = Docente.objects.get(usuario__rut=rut_docente)
            if not verificar_especialidad_docente(nombre_asignatura, docente.especialidad.nombre):
                print(f"⛔ Docente {rut_docente} no puede impartir {nombre_asignatura} (especialidad: {docente.especialidad.nombre})")
                continue

            curso = Curso.objects.get(nivel=nivel, letra=letra)
            
            # Determinar sala
            sala_especial = get_sala_especial(nombre_asignatura)
            sala = sala_especial if sala_especial else get_sala_por_curso(nivel, letra)
            
            # Crear asignatura impartida
            asignatura_impartida, created = AsignaturaImpartida.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'asignatura': asignatura_obj,
                    'docente': docente
                }
            )
            
            clases_creadas = 0
            horarios_usados = []
            
            # Intentar usar horarios originales primero
            for dia, bloque_inicio in horarios_originales:
                sin_conflictos, mensaje = verificar_conflictos_bloques_consecutivos(
                    dia, bloque_inicio, docente, curso, sala
                )
                
                if sin_conflictos:
                    # Crear clases para ambos bloques consecutivos
                    for i in range(2):
                        bloque = str(int(bloque_inicio) + i)
                    clase, created = Clase.objects.get_or_create(
                        asignatura_impartida=asignatura_impartida,
                        curso=curso,
                        fecha=dia,
                            horario=bloque,
                        sala=sala
                    )
                    if created:
                        clases_creadas += 1
                    horarios_usados.append((dia, bloque_inicio))
                    break
            
            # Si no se pudo usar horarios originales, buscar alternativos
            if not horarios_usados:
                horarios_disponibles = obtener_horarios_disponibles_bloques_consecutivos(docente, curso, sala)
                
                for dia, bloque_inicio in horarios_disponibles:
                    sin_conflictos, _ = verificar_conflictos_bloques_consecutivos(
                        dia, bloque_inicio, docente, curso, sala
                    )
                    
                    if sin_conflictos:
                        # Crear clases para ambos bloques consecutivos
                        for i in range(2):
                            bloque = str(int(bloque_inicio) + i)
                            clase, created = Clase.objects.get_or_create(
                                asignatura_impartida=asignatura_impartida,
                                curso=curso,
                                fecha=dia,
                                horario=bloque,
                                sala=sala
                            )
                            if created:
                                clases_creadas += 1
                        horarios_usados.append((dia, bloque_inicio))
                        conflictos_resueltos += 1
                        break
                    
            if clases_creadas > 0:
                asignaturas_creadas += 1
                horarios_str = ", ".join([f"{dia} {bloque}-{int(bloque)+1}" for dia, bloque in horarios_usados])
                print(f"✅ {codigo} ({nombre_asignatura}): {clases_creadas} clases en {horarios_str}")
            else:
                print(f"❌ No se pudo crear {codigo} ({nombre_asignatura}) - sin horarios disponibles")
            
        except Exception as e:
            print(f"❌ Error al crear {codigo}: {str(e)}")

    print(f"\n📊 Resumen:")
    print(f"- Total de asignaturas impartidas creadas: {asignaturas_creadas}")
    print(f"- Conflictos resueltos automáticamente: {conflictos_resueltos}")
    print(f"- Asignaturas electivas omitidas: ✓")
    print(f"- Bloques consecutivos implementados: ✓")
    print(f"- Verificación de especialidades: ✓")

if __name__ == "__main__":
    crear_asignaturas_impartidas()