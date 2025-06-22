import os
import django
import sys

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models.cursos import Curso, Clase

def mostrar_horario_1A():
    """
    Muestra el horario del curso 1°A de forma simple
    """
    try:
        # Obtener el curso 1°A
        curso = Curso.objects.get(nivel=1, letra='A')
        print(f"\n{'='*60}")
        print(f"HORARIO DEL CURSO {curso}")
        print(f"{'='*60}")
        
        # Obtener todas las clases del curso 1°A
        clases = Clase.objects.filter(
            curso=curso
        ).select_related(
            'asignatura_impartida__asignatura',
            'asignatura_impartida__docente__usuario'
        ).order_by('fecha', 'horario')
        
        if clases.exists():
            print(f"\nTotal de clases: {clases.count()}")
            print("\nCLASES DEL CURSO 1°A:")
            print("-" * 60)
            
            for clase in clases:
                print(f"• {clase.asignatura_impartida.asignatura.nombre}")
                print(f"  - Docente: {clase.asignatura_impartida.docente.usuario.nombre} {clase.asignatura_impartida.docente.usuario.apellido_paterno}")
                print(f"  - Día: {clase.fecha}")
                print(f"  - Horario: {clase.horario}")
                print(f"  - Sala: {clase.sala}")
                print(f"  - Código: {clase.asignatura_impartida.codigo}")
                print()
        else:
            print("❌ No se encontraron clases para el curso 1°A")
            
    except Curso.DoesNotExist:
        print("❌ Error: No se encontró el curso 1°A en la base de datos")
    except Exception as e:
        print(f"❌ Error al consultar el horario: {str(e)}")

if __name__ == "__main__":
    mostrar_horario_1A() 