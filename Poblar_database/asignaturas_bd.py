import os
import django
import sys
from datetime import date

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Asignatura, EvaluacionBase

# Lista de asignaturas con su tipo (obligatoria o electiva) y nivel
asignaturas_data = [
    # Opcion por determinado
    ("Ninguna", False, 1),

    # Asignaturas Obligatorias 1° y 2° medio
    ("Lenguaje", False, 1),
    ("Matemáticas", False, 1),
    ("Historia", False, 1),
    ("Biología", False, 1),
    ("Física", False, 1),
    ("Química", False, 1),
    ("Inglés", False, 1),
    ("Educación Física", False, 1),
    ("Arte", False, 1),
    ("Música", False, 1),
    ("Tecnología", False, 1),

    ("Lenguaje", False, 2),
    ("Matemáticas", False, 2),
    ("Historia", False, 2),
    ("Biología", False, 2),
    ("Física", False, 2),
    ("Química", False, 2),
    ("Inglés", False, 2),
    ("Educación Física", False, 2),
    ("Arte", False, 2),
    ("Música", False, 2),
    ("Tecnología", False, 2),

    # Asignaturas Obligatorias 3° y 4° medio
    ("Lenguaje", False, 3),
    ("Matemáticas", False, 3),
    ("Historia", False, 3),
    ("Biología", False, 3),
    ("Física", False, 3),
    ("Química", False, 3),
    ("Inglés", False, 3),
    ("Educación Física", False, 3),
    ("Filosofía", False, 3),

    ("Lenguaje", False, 4),
    ("Matemáticas", False, 4),
    ("Historia", False, 4),
    ("Biología", False, 4),
    ("Física", False, 4),
    ("Química", False, 4),
    ("Inglés", False, 4),
    ("Educación Física", False, 4),
    ("Filosofía", False, 4),

    # Electivos 3° medio
    ("Filosofía y Ética", True, 3),
    ("Literatura y Escritura Creativa", True, 3),
    ("Biología Avanzada", True, 3),
    ("Química Experimental", True, 3),

    # Electivos 4° medio
    ("Psicología y Desarrollo Humano", True, 4),
    ("Sociología y Estudios Sociales", True, 4),
    ("Física Aplicada", True, 4),
    ("Matemática Avanzada", True, 4)
]

# Crear asignaturas y evaluaciones base
for nombre, es_electivo, nivel in asignaturas_data:
    asignatura, created = Asignatura.objects.get_or_create(
        nombre=nombre,
        nivel=nivel,  # Agregamos nivel a la búsqueda para permitir la misma asignatura en diferentes niveles
        defaults={
            "es_electivo": es_electivo
        }
    )

    if not created:
        # Si ya existe, aseguramos que el tipo esté actualizado
        asignatura.es_electivo = es_electivo
        asignatura.save()

    if nombre != "Ninguna":
        # Evaluaciones base predeterminadas
        evaluaciones = [
            ("Prueba 1", 30.0, "Primera prueba parcial"),
            ("Prueba 2", 30.0, "Segunda prueba parcial"),
            ("Examen Final", 40.0, "Examen final del curso"),
        ]
        for nombre_eval, peso, desc in evaluaciones:
            EvaluacionBase.objects.get_or_create(
                asignatura=asignatura,
                nombre=nombre_eval,
                defaults={"ponderacion": peso, "descripcion": desc}
            )

print("✅ Asignaturas y evaluaciones base creadas o actualizadas exitosamente.")
