import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Docente, Especialidad, Asignatura

print('================ DOCENTES ================')
for docente in Docente.objects.all():
    nombre = f"{docente.usuario.nombre} {docente.usuario.apellido_paterno} {docente.usuario.apellido_materno}" if hasattr(docente.usuario, 'nombre') else str(docente.usuario)
    especialidad = docente.especialidad.nombre if docente.especialidad else 'Sin especialidad'
    print(f"- {nombre} | Especialidad: {especialidad}")

print('\n================ ESPECIALIDADES ================')
for esp in Especialidad.objects.all():
    print(f"- {esp.nombre}")

print('\n================ ASIGNATURAS ================')
for asig in Asignatura.objects.all():
    tipo = 'Electivo' if asig.es_electivo else 'Obligatoria'
    print(f"- {asig.nombre} | Nivel: {asig.nivel} | {tipo}") 