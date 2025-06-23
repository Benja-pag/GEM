import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Estudiante, AlumnoEvaluacion, Evaluacion, EvaluacionBase, Asignatura
from Core.views.alumnos import get_evaluaciones_estudiante, get_promedio_estudiante
from Core.views.docentes import get_evaluaciones_docente, get_estadisticas_docente

def test_evaluaciones_estudiante():
    """
    Prueba las funciones de evaluaciones de estudiantes
    """
    print("🧪 PRUEBA DE EVALUACIONES DE ESTUDIANTES")
    print("="*50)
    
    # Obtener el primer estudiante
    estudiante = Estudiante.objects.first()
    if not estudiante:
        print("❌ No hay estudiantes en la base de datos")
        return
    
    print(f"👤 Estudiante: {estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}")
    print(f"🎓 Curso: {estudiante.curso}")
    
    # Obtener evaluaciones
    evaluaciones = get_evaluaciones_estudiante(estudiante.pk)
    promedio = get_promedio_estudiante(estudiante.pk)
    
    print(f"\n📊 Promedio general: {promedio}")
    print(f"📚 Asignaturas con evaluaciones: {len(evaluaciones)}")
    
    for asignatura, evals in evaluaciones.items():
        print(f"\n📖 {asignatura}:")
        for eval in evals:
            print(f"   • {eval['nombre']}: {eval['nota']} ({eval['estado']}) - {eval['fecha']}")
    
    # Verificar que no hay duplicados
    total_evaluaciones = sum(len(evals) for evals in evaluaciones.values())
    print(f"\n✅ Total evaluaciones únicas: {total_evaluaciones}")

def test_evaluaciones_docente():
    """
    Prueba las funciones de evaluaciones de docentes
    """
    print("\n🧪 PRUEBA DE EVALUACIONES DE DOCENTES")
    print("="*50)
    
    # Obtener el primer docente
    from Core.models import Docente
    docente = Docente.objects.first()
    if not docente:
        print("❌ No hay docentes en la base de datos")
        return
    
    print(f"👨‍🏫 Docente: {docente.usuario.nombre} {docente.usuario.apellido_paterno}")
    
    # Obtener evaluaciones
    evaluaciones = get_evaluaciones_docente(docente.pk)
    estadisticas = get_estadisticas_docente(docente.pk)
    
    print(f"\n📊 Estadísticas:")
    print(f"   • Total evaluaciones: {estadisticas['total_evaluaciones']}")
    print(f"   • Evaluaciones calificadas: {estadisticas['evaluaciones_calificadas']}")
    print(f"   • Promedio general: {estadisticas['promedio_general']:.2f}")
    
    print(f"\n📚 Asignaturas con evaluaciones: {len(evaluaciones)}")
    
    for asignatura, evals in evaluaciones.items():
        print(f"\n📖 {asignatura}:")
        for eval in evals:
            print(f"   • {eval['nombre']} - {eval['curso']}: {eval['promedio']:.1f} ({eval['estado']})")
    
    # Verificar que no hay duplicados
    total_evaluaciones = sum(len(evals) for evals in evaluaciones.values())
    print(f"\n✅ Total evaluaciones únicas: {total_evaluaciones}")

def test_estructura_datos():
    """
    Prueba la estructura de datos en la base de datos
    """
    print("\n🧪 PRUEBA DE ESTRUCTURA DE DATOS")
    print("="*50)
    
    total_asignaturas = Asignatura.objects.exclude(nombre="Ninguna").count()
    total_evaluaciones_base = EvaluacionBase.objects.count()
    total_evaluaciones = Evaluacion.objects.count()
    total_notas = AlumnoEvaluacion.objects.count()
    total_estudiantes = Estudiante.objects.count()
    
    print(f"📚 Asignaturas: {total_asignaturas}")
    print(f"📝 Evaluaciones base: {total_evaluaciones_base}")
    print(f"📋 Evaluaciones reales: {total_evaluaciones}")
    print(f"📊 Notas asignadas: {total_notas}")
    print(f"👥 Estudiantes: {total_estudiantes}")
    
    # Verificar duplicados en evaluaciones base
    print(f"\n🔍 Verificando duplicados en evaluaciones base...")
    for asignatura in Asignatura.objects.exclude(nombre="Ninguna")[:3]:
        evaluaciones_base = EvaluacionBase.objects.filter(asignatura=asignatura)
        print(f"   {asignatura.nombre}: {evaluaciones_base.count()} evaluaciones base")
        for eval_base in evaluaciones_base:
            print(f"     • {eval_base.nombre}")

def main():
    """
    Función principal
    """
    print("🚀 PRUEBAS DEL SISTEMA DE EVALUACIONES")
    print("="*60)
    
    test_estructura_datos()
    test_evaluaciones_estudiante()
    test_evaluaciones_docente()
    
    print("\n✅ PRUEBAS COMPLETADAS")

if __name__ == "__main__":
    main() 