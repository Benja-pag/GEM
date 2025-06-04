import os
import django
import sys
# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models.calendarios import HorarioCurso
from Core.models.cursos import Curso
from django.core.exceptions import ObjectDoesNotExist

def crear_horarios():
    horario_lunes_a_jueves = [
        {"actividad": "Clase", "hora_inicio": "08:00", "hora_fin": "08:45"},
        {"actividad": "Clase", "hora_inicio": "08:45", "hora_fin": "09:30"},
        {"actividad": "Recreo", "hora_inicio": "09:30", "hora_fin": "09:45"},
        {"actividad": "Clase", "hora_inicio": "09:45", "hora_fin": "10:30"},
        {"actividad": "Clase", "hora_inicio": "10:30", "hora_fin": "11:15"},
        {"actividad": "Recreo", "hora_inicio": "11:15", "hora_fin": "11:30"},
        {"actividad": "Clase", "hora_inicio": "11:30", "hora_fin": "12:15"},
        {"actividad": "Clase", "hora_inicio": "12:15", "hora_fin": "13:00"},
        {"actividad": "Almuerzo", "hora_inicio": "13:00", "hora_fin": "13:45"},
        {"actividad": "Clase", "hora_inicio": "13:45", "hora_fin": "14:30"},
        {"actividad": "Clase", "hora_inicio": "14:30", "hora_fin": "15:15"},
        {"actividad": "Clase", "hora_inicio": "15:15", "hora_fin": "16:00"},
    ]

    horario_viernes = [
        {"actividad": "Clase", "hora_inicio": "08:00", "hora_fin": "08:45"},
        {"actividad": "Clase", "hora_inicio": "08:45", "hora_fin": "09:30"},
        {"actividad": "Recreo", "hora_inicio": "09:30", "hora_fin": "09:45"},
        {"actividad": "Clase", "hora_inicio": "09:45", "hora_fin": "10:30"},
        {"actividad": "Clase", "hora_inicio": "10:30", "hora_fin": "11:15"},
        {"actividad": "Recreo", "hora_inicio": "11:15", "hora_fin": "11:30"},
        {"actividad": "Clase", "hora_inicio": "11:30", "hora_fin": "12:15"},
        {"actividad": "Clase", "hora_inicio": "12:15", "hora_fin": "13:00"},
    ]

    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves']
    
    # Obtener todos los cursos
    cursos = Curso.objects.all()
    
    # Crear horarios para cada curso
    for curso in cursos:
        # Crear horarios de lunes a jueves
        for dia in dias_semana:
            for bloque in horario_lunes_a_jueves:
                HorarioCurso.objects.create(
                    curso=curso,
                    actividad=bloque['actividad'],
                    dia=dia,
                    hora_inicio=bloque['hora_inicio'],
                    hora_fin=bloque['hora_fin']
                )
        
        # Crear horario del viernes
        for bloque in horario_viernes:
            HorarioCurso.objects.create(
                curso=curso,
                actividad=bloque['actividad'],
                dia='Viernes',
                hora_inicio=bloque['hora_inicio'],
                hora_fin=bloque['hora_fin']
            )

    print("✅ Horarios creados exitosamente para todos los cursos")

if __name__ == "__main__":
    crear_horarios() 