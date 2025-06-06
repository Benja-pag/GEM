import os
import django
import sys
from datetime import date

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Estudiante, AsignaturaImpartida, AsignaturaInscrita

def inscribir_asignaturas():
    try:
        # Obtener todos los estudiantes
        estudiantes = Estudiante.objects.all()
        print(f"Procesando {estudiantes.count()} estudiantes...")
        
        # Contador para seguimiento
        asignaturas_inscritas = 0
        
        # Para cada estudiante
        for estudiante in estudiantes:
            if estudiante.curso:
                # Obtener todas las asignaturas impartidas para el nivel del curso
                asignaturas_impartidas = AsignaturaImpartida.objects.filter(
                    asignatura__nivel=estudiante.curso.nivel
                )
                
                # Inscribir al estudiante en cada asignatura
                for asignatura_impartida in asignaturas_impartidas:
                    # Crear la inscripción solo si no existe
                    inscripcion, created = AsignaturaInscrita.objects.get_or_create(
                        estudiante=estudiante,
                        asignatura_impartida=asignatura_impartida,
                        defaults={'validada': True}  # Las inscripciones automáticas se validan por defecto
                    )
                    if created:
                        asignaturas_inscritas += 1
                        print(f"✓ {estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno} inscrito en {asignatura_impartida.asignatura.nombre}")
        
        print(f"\n✅ Proceso completado:")
        print(f"- Total de estudiantes procesados: {estudiantes.count()}")
        print(f"- Total de asignaturas inscritas: {asignaturas_inscritas}")
        
    except Exception as e:
        print(f"❌ Error al inscribir asignaturas: {str(e)}")

if __name__ == '__main__':
    inscribir_asignaturas()

