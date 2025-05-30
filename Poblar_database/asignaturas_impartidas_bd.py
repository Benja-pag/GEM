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