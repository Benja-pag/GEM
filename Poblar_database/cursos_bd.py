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
cursos_data = [ 
    {'nivel': 1, 'letra': 'A'},
    {'nivel': 1, 'letra': 'B'},
    {'nivel': 2, 'letra': 'A'},
    {'nivel': 2, 'letra': 'B'},
    {'nivel': 3, 'letra': 'A'},
    {'nivel': 3, 'letra': 'B'},
    {'nivel': 4, 'letra': 'A'},
    {'nivel': 4, 'letra': 'B'},
    ]


cursos = []
for data in cursos_data:
    curso, _ = Curso.objects.get_or_create(nivel=data['nivel'], letra=data['letra'])
    cursos.append(curso)

print("✅ Cursos creados exitosamente.")