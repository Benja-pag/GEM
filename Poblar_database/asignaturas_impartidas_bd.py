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

# Datos de asignaturas impartidas
asignaturas_impartidas_data = [
    # Formato: (código, asignatura_nombre, rut_docente, nivel)
    # 1° Medio A
    ("LEN1A", "Lenguaje", "15345638", 1),
    ("MAT1A", "Matemáticas", "15456786", 1),
    ("HIS1A", "Historia", "15654321", 1),
    ("BIO1A", "Biología", "15543210", 1),
    ("FIS1A", "Física", "15432109", 1),
    ("QUI1A", "Química", "16321098", 1),
    ("ING1A", "Inglés", "16176543", 1),
    ("EFI1A", "Educación Física", "16276543", 1),
    ("ART1A", "Arte", "16376543", 1),
    ("MUS1A", "Música", "16476543", 1),
    ("TEC1A", "Tecnología", "16576543", 1),
    
    # 1° Medio B
    ("LEN1B", "Lenguaje", "15345638", 1),
    ("MAT1B", "Matemáticas", "15456786", 1),
    ("HIS1B", "Historia", "15654321", 1),
    ("BIO1B", "Biología", "15543210", 1),
    ("FIS1B", "Física", "15432109", 1),
    ("QUI1B", "Química", "16321098", 1),
    ("ING1B", "Inglés", "16176543", 1),
    ("EFI1B", "Educación Física", "16276543", 1),
    ("ART1B", "Arte", "16376543", 1),
    ("MUS1B", "Música", "16476543", 1),
    ("TEC1B", "Tecnología", "16576543", 1),
    
    # 2° Medio A
    ("LEN2A", "Lenguaje", "16676543", 2),
    ("MAT2A", "Matemáticas", "17776543", 2),
    ("HIS2A", "Historia", "17888888", 2),
    ("BIO2A", "Biología", "17999999", 2),
    ("FIS2A", "Física", "17111111", 2),
    ("QUI2A", "Química", "17121212", 2),
    ("ING2A", "Inglés", "18579135", 2),
    ("EFI2A", "Educación Física", "18680246", 2),
    ("ART2A", "Arte", "18791357", 2),
    ("MUS2A", "Música", "18802468", 2),
    ("TEC2A", "Tecnología", "18913579", 2),
    
    # 2° Medio B
    ("LEN2B", "Lenguaje", "16676543", 2),
    ("MAT2B", "Matemáticas", "17776543", 2),
    ("HIS2B", "Historia", "17888888", 2),
    ("BIO2B", "Biología", "17999999", 2),
    ("FIS2B", "Física", "17111111", 2),
    ("QUI2B", "Química", "17121212", 2),
    ("ING2B", "Inglés", "18579135", 2),
    ("EFI2B", "Educación Física", "18680246", 2),
    ("ART2B", "Arte", "18791357", 2),
    ("MUS2B", "Música", "18802468", 2),
    ("TEC2B", "Tecnología", "18913579", 2),
    
    # 3° Medio A
    ("LEN3A", "Lenguaje", "19024680", 3),
    ("MAT3A", "Matemáticas", "19135791", 3),
    ("HIS3A", "Historia", "15345638", 3),
    ("BIO3A", "Biología", "15456786", 3),
    ("FIS3A", "Física", "15654321", 3),
    ("QUI3A", "Química", "15543210", 3),
    ("ING3A", "Inglés", "15432109", 3),
    ("EFI3A", "Educación Física", "16321098", 3),
    ("FIL3A", "Filosofía", "16176543", 3),
    
    # 3° Medio B
    ("LEN3B", "Lenguaje", "19024680", 3),
    ("MAT3B", "Matemáticas", "19135791", 3),
    ("HIS3B", "Historia", "15345638", 3),
    ("BIO3B", "Biología", "15456786", 3),
    ("FIS3B", "Física", "15654321", 3),
    ("QUI3B", "Química", "15543210", 3),
    ("ING3B", "Inglés", "15432109", 3),
    ("EFI3B", "Educación Física", "16321098", 3),
    ("FIL3B", "Filosofía", "16176543", 3),
    
    # 4° Medio A
    ("LEN4A", "Lenguaje", "16276543", 4),
    ("MAT4A", "Matemáticas", "16376543", 4),
    ("HIS4A", "Historia", "16476543", 4),
    ("BIO4A", "Biología", "16576543", 4),
    ("FIS4A", "Física", "16676543", 4),
    ("QUI4A", "Química", "17776543", 4),
    ("ING4A", "Inglés", "17888888", 4),
    ("EFI4A", "Educación Física", "17999999", 4),
    ("FIL4A", "Filosofía", "17111111", 4),
    
    # 4° Medio B
    ("LEN4B", "Lenguaje", "16276543", 4),
    ("MAT4B", "Matemáticas", "16376543", 4),
    ("HIS4B", "Historia", "16476543", 4),
    ("BIO4B", "Biología", "16576543", 4),
    ("FIS4B", "Física", "16676543", 4),
    ("QUI4B", "Química", "17776543", 4),
    ("ING4B", "Inglés", "17888888", 4),
    ("EFI4B", "Educación Física", "17999999", 4),
    ("FIL4B", "Filosofía", "17111111", 4),
    
    # Electivos 3° Medio
    ("FIL-E3", "Filosofía y Ética", "17121212", 3),
    ("LIT-E3", "Literatura y Escritura Creativa", "18579135", 3),
    ("BIO-E3", "Biología Avanzada", "18680246", 3),
    ("QUI-E3", "Química Experimental", "18791357", 3),
    
    # Electivos 4° Medio
    ("PSI-E4", "Psicología y Desarrollo Humano", "18802468", 4),
    ("SOC-E4", "Sociología y Estudios Sociales", "18913579", 4),
    ("FIS-E4", "Física Aplicada", "19024680", 4),
    ("MAT-E4", "Matemática Avanzada", "19135791", 4)
]

# Crear asignaturas impartidas
for codigo, nombre_asignatura, rut_docente, nivel in asignaturas_impartidas_data:
    try:
        # Obtener la asignatura y el docente
        asignatura = Asignatura.objects.get(nombre=nombre_asignatura, nivel=nivel)
        docente = Docente.objects.get(usuario__rut=rut_docente)
        
        # Crear o actualizar la asignatura impartida
        asignatura_impartida, created = AsignaturaImpartida.objects.get_or_create(
            codigo=codigo,
            defaults={
                'asignatura': asignatura,
                'docente': docente
            }
        )
        
        if not created:
            # Actualizar los campos si ya existía
            asignatura_impartida.asignatura = asignatura
            asignatura_impartida.docente = docente
            asignatura_impartida.save()
            
    except Asignatura.DoesNotExist:
        print(f"⚠️ No se encontró la asignatura: {nombre_asignatura} nivel {nivel}")
    except Docente.DoesNotExist:
        print(f"⚠️ No se encontró el docente con RUT: {rut_docente}")
    except Exception as e:
        print(f"⚠️ Error al crear asignatura impartida {codigo}: {str(e)}")

print("✅ Asignaturas impartidas creadas o actualizadas exitosamente")