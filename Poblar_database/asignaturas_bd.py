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

# Lista de asignaturas con su tipo (obligatoria o electiva)
asignaturas_nombres = [
    # 00 - General
    ("Ninguna", False),

    # 01-10 - Asignaturas Obligatorias
    ("Matemáticas", False),
    ("Lenguaje", False),
    ("Historia", False),
    ("Biología", False),
    ("Física", False),
    ("Química", False),
    ("Inglés", False),
    ("Educación Física", False),
    ("Arte", False),
    ("Tecnología", False),

    # 11-20 - Electivos Humanistas
    ("Filosofía y Ética", True),
    ("Literatura y Escritura Creativa", True),
    ("Historia del Arte y Cultura", True),
    ("Psicología y Desarrollo Humano", True),
    ("Sociología y Estudios Sociales", True),
    ("Teatro y Expresión Corporal", True),
    ("Música y Composición", True),
    ("Taller de Debate y Oratoria", True),
    ("Educación Ambiental y Sostenibilidad", True),
    ("Derechos Humanos y Ciudadanía", True),

    # 21-30 - Electivos Científicos
    ("Biología Avanzada", True),
    ("Química Experimental", True),
    ("Física Aplicada", True),
    ("Matemáticas Discretas", True),
    ("Programación y Robótica", True),
    ("Astronomía y Ciencias del Espacio", True),
    ("Investigación Científica y Método Experimental", True),
    ("Tecnología e Innovación", True),
    ("Ciencias de la Tierra y Medio Ambiente", True),
    ("Estadística y Análisis de Datos", True),
]

# Crear asignaturas y evaluaciones base
for nombre, es_electivo in asignaturas_nombres:
    asignatura, created = Asignatura.objects.get_or_create(
        nombre=nombre,
        defaults={"es_electivo": es_electivo}
    )
    
    if nombre != "Ninguna":
        EvaluacionBase.objects.get_or_create(
            asignatura=asignatura,
            nombre="Prueba 1",
            defaults={"ponderacion": 30.0, "descripcion": "Primera prueba parcial"}
        )
        EvaluacionBase.objects.get_or_create(
            asignatura=asignatura,
            nombre="Prueba 2",
            defaults={"ponderacion": 30.0, "descripcion": "Segunda prueba parcial"}
        )
        EvaluacionBase.objects.get_or_create(
            asignatura=asignatura,
            nombre="Examen Final",
            defaults={"ponderacion": 40.0, "descripcion": "Examen final del curso"}
        )

print("✅ Asignaturas y evaluaciones base creadas exitosamente.")
