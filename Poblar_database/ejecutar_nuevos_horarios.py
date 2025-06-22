import os
import django
import sys

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from asignaturas_impartidas_bd import crear_asignaturas_impartidas
from Core.models import Docente, Asignatura, Curso

def verificar_disponibilidad_docentes():
    """Verifica que hay suficientes docentes para las asignaturas obligatorias"""
    print("🔍 Verificando disponibilidad de docentes...")
    
    # Obtener asignaturas obligatorias por nivel
    asignaturas_obligatorias = {
        1: ["Lenguaje", "Matemáticas", "Historia", "Biología", "Física", "Química", "Inglés", "Educación Física", "Arte", "Música", "Tecnología"],
        2: ["Lenguaje", "Matemáticas", "Historia", "Biología", "Física", "Química", "Inglés", "Educación Física", "Arte", "Música", "Tecnología"],
        3: ["Lenguaje", "Matemáticas", "Historia", "Biología", "Física", "Química", "Inglés", "Educación Física", "Filosofía"],
        4: ["Lenguaje", "Matemáticas", "Historia", "Biología", "Física", "Química", "Inglés", "Educación Física", "Filosofía"]
    }
    
    # Obtener docentes por especialidad
    docentes_por_especialidad = {}
    for docente in Docente.objects.select_related('especialidad').all():
        especialidad = docente.especialidad.nombre
        if especialidad not in docentes_por_especialidad:
            docentes_por_especialidad[especialidad] = []
        docentes_por_especialidad[especialidad].append(docente)
    
    print(f"📊 Docentes disponibles por especialidad:")
    for especialidad, docentes in docentes_por_especialidad.items():
        print(f"  - {especialidad}: {len(docentes)} docentes")
    
    # Verificar cobertura por nivel
    for nivel, asignaturas in asignaturas_obligatorias.items():
        print(f"\n📚 Nivel {nivel}:")
        for asignatura in asignaturas:
            # Buscar docentes que pueden impartir esta asignatura
            docentes_disponibles = []
            for especialidad, docentes in docentes_por_especialidad.items():
                if verificar_especialidad_docente(asignatura, especialidad):
                    docentes_disponibles.extend(docentes)
            
            if docentes_disponibles:
                print(f"  ✅ {asignatura}: {len(docentes_disponibles)} docentes disponibles")
            else:
                print(f"  ❌ {asignatura}: SIN DOCENTES DISPONIBLES")
    
    return True

def verificar_especialidad_docente(nombre_asignatura, especialidad_docente):
    """Verifica si un docente puede impartir una asignatura según su especialidad"""
    equivalencias = {
        "Matematicas": ["Matemáticas", "Matemática Avanzada", "Matemáticas Discretas", "Estadística y Análisis de Datos"],
        "Lenguaje": ["Lenguaje", "Literatura y Escritura Creativa"],
        "Historia": ["Historia", "Historia del Arte y Cultura", "Sociología y Estudios Sociales"],
        "Biologia": ["Biología", "Biología Avanzada", "Ciencias de la Tierra y Medio Ambiente"],
        "Fisica": ["Física", "Física Aplicada", "Astronomía y Ciencias del Espacio"],
        "Quimica": ["Química", "Química Experimental"],
        "Ingles": ["Inglés"],
        "Educación Fisica": ["Educación Física"],
        "Arte": ["Arte", "Historia del Arte y Cultura", "Teatro y Expresión Corporal"],
        "Tecnologia": ["Tecnología", "Tecnología e Innovación", "Programación y Robótica"],
        "Filosofía y Ética": ["Filosofía", "Filosofía y Ética"],
        "Psicología y Desarrollo Humano": ["Psicología y Desarrollo Humano"],
        "Música y Composición": ["Música"],
        "Investigación Científica y Método Experimental": ["Biología Avanzada", "Química Experimental", "Física Aplicada"],
    }
    
    if especialidad_docente in equivalencias:
        return nombre_asignatura in equivalencias[especialidad_docente]
    
    return False

def main():
    """Función principal que ejecuta el nuevo sistema de horarios"""
    print("🚀 Iniciando nuevo sistema de horarios con bloques consecutivos")
    print("=" * 60)
    
    # Verificar disponibilidad de docentes
    verificar_disponibilidad_docentes()
    
    print("\n" + "=" * 60)
    print("🔄 Creando asignaturas impartidas...")
    
    # Crear las asignaturas impartidas con el nuevo sistema
    crear_asignaturas_impartidas()
    
    print("\n" + "=" * 60)
    print("✅ Proceso completado exitosamente!")
    print("\n📋 Resumen de mejoras implementadas:")
    print("  ✓ Bloques consecutivos (2 bloques seguidos por asignatura)")
    print("  ✓ Verificación de conflictos entre profesores")
    print("  ✓ Exclusión de asignaturas electivas")
    print("  ✓ Verificación de especialidades de docentes")
    print("  ✓ Asignación automática de salas especiales")
    print("  ✓ Resolución automática de conflictos de horarios")

if __name__ == "__main__":
    main() 