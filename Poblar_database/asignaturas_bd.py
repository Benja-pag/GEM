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
asignaturas_nombres = [
    # (Nombre, es_electivo, nivel)
    ("Ninguna", False, 1),
    ("Matemáticas", False, 1),
    ("Lenguaje", False, 1),
    ("Historia", False, 1),
    ("Biología", False, 2),
    ("Física", False, 2),
    ("Química", False, 3),
    ("Inglés", False, 1),
    ("Educación Física", False, 1),
    ("Arte", False, 1),
    ("Tecnología", False, 2),
    ("Filosofía y Ética", True, 3),
    ("Literatura y Escritura Creativa", True, 3),
    ("Historia del Arte y Cultura", True, 3),
    ("Psicología y Desarrollo Humano", True, 4),
    ("Sociología y Estudios Sociales", True, 4),
    ("Teatro y Expresión Corporal", True, 3),
    ("Música y Composición", True, 3),
    ("Taller de Debate y Oratoria", True, 4),
    ("Educación Ambiental y Sostenibilidad", True, 4),
    ("Derechos Humanos y Ciudadanía", True, 4),
    ("Biología Avanzada", True, 3),
    ("Química Experimental", True, 3),
    ("Física Aplicada", True, 3),
    ("Matemáticas Discretas", True, 4),
    ("Programación y Robótica", True, 4),
    ("Astronomía y Ciencias del Espacio", True, 4),
    ("Investigación Científica y Método Experimental", True, 4),
    ("Tecnología e Innovación", True, 4),
    ("Ciencias de la Tierra y Medio Ambiente", True, 4),
    ("Estadística y Análisis de Datos", True, 4),
]

# Crear asignaturas y evaluaciones base
for nombre, es_electivo, nivel in asignaturas_nombres:
    asignatura, created = Asignatura.objects.get_or_create(
        nombre=nombre,
        defaults={
            "es_electivo": es_electivo,
            "nivel": nivel,
        }
    )

    if not created:
        # Si ya existe, aseguramos que el nivel esté actualizado
        asignatura.es_electivo = es_electivo
        asignatura.nivel = nivel
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
