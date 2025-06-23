import os
import django
import sys
from datetime import date, time

# Agrega el directorio raíz del proyecto al path (sube dos niveles desde subcarpeta)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models.calendarios import HorarioCurso

def crear_horarios():
    # Definir los bloques y sus actividades
    bloques_lunes_a_jueves = [
        {'bloque': '1', 'actividad': 'CLASE'},
        {'bloque': '2', 'actividad': 'CLASE'},
        {'bloque': 'RECREO1', 'actividad': 'RECREO'},
        {'bloque': '3', 'actividad': 'CLASE'},
        {'bloque': '4', 'actividad': 'CLASE'},
        {'bloque': 'RECREO2', 'actividad': 'RECREO'},
        {'bloque': '5', 'actividad': 'CLASE'},
        {'bloque': '6', 'actividad': 'CLASE'},
        {'bloque': 'ALMUERZO', 'actividad': 'ALMUERZO'},
        {'bloque': '7', 'actividad': 'CLASE'},
        {'bloque': '8', 'actividad': 'CLASE'},
        {'bloque': '9', 'actividad': 'CLASE'},
    ]

    bloques_viernes = [
        {'bloque': '1', 'actividad': 'CLASE'},
        {'bloque': '2', 'actividad': 'CLASE'},
        {'bloque': 'RECREO1', 'actividad': 'RECREO'},
        {'bloque': '3', 'actividad': 'CLASE'},
        {'bloque': '4', 'actividad': 'CLASE'},
        {'bloque': 'RECREO2', 'actividad': 'RECREO'},
        {'bloque': '5', 'actividad': 'CLASE'},
        {'bloque': '6', 'actividad': 'CLASE'},
    ]

    dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES']
    
    # Crear horarios de lunes a jueves
    for dia in dias:
        for bloque in bloques_lunes_a_jueves:
            HorarioCurso.objects.get_or_create(
                bloque=bloque['bloque'],
                dia=dia,
                actividad=bloque['actividad']
            )
    
    # Crear horario del viernes
    for bloque in bloques_viernes:
        HorarioCurso.objects.get_or_create(
            bloque=bloque['bloque'],
            dia='VIERNES',
            actividad=bloque['actividad']
        )

    print("✅ Horarios base creados exitosamente")

if __name__ == "__main__":
    crear_horarios() 