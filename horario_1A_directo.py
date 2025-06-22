import os
import django
import sys

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models.cursos import Curso, Clase

print("="*70)
print("HORARIO DEL CURSO 1°A - CONSULTA DIRECTA")
print("="*70)

try:
    # Obtener el curso 1°A
    curso = Curso.objects.get(nivel=1, letra='A')
    print(f"\nCurso encontrado: {curso}")
    
    # Obtener todas las clases del curso 1°A
    clases = Clase.objects.filter(
        curso=curso
    ).select_related(
        'asignatura_impartida__asignatura',
        'asignatura_impartida__docente__usuario'
    ).order_by('fecha', 'horario')
    
    if clases.exists():
        print(f"\nTotal de clases encontradas: {clases.count()}")
        print("\n" + "="*70)
        print("DETALLE DE CLASES:")
        print("="*70)
        
        for i, clase in enumerate(clases, 1):
            print(f"\n{i}. {clase.asignatura_impartida.asignatura.nombre}")
            print(f"   Docente: {clase.asignatura_impartida.docente.usuario.nombre} {clase.asignatura_impartida.docente.usuario.apellido_paterno}")
            print(f"   Día: {clase.fecha}")
            print(f"   Horario: {clase.horario}")
            print(f"   Sala: {clase.sala}")
            print(f"   Código: {clase.asignatura_impartida.codigo}")
            print("-" * 50)
    else:
        print("\n❌ No se encontraron clases para el curso 1°A")
        print("Esto puede indicar que:")
        print("- El curso no tiene clases asignadas")
        print("- Las clases no están vinculadas al curso")
        print("- La base de datos no tiene datos de horarios")
        
except Curso.DoesNotExist:
    print("\n❌ Error: No se encontró el curso 1°A en la base de datos")
    print("Verifique que el curso 1°A exista en la base de datos")
    
except Exception as e:
    print(f"\n❌ Error al consultar el horario: {str(e)}")
    print("Verifique la configuración de Django y la base de datos")

print("\n" + "="*70)
print("FIN DE LA CONSULTA")
print("="*70) 