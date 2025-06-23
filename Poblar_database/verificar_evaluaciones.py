import os
import django
import sys
from django.db import models

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import (
    Asignatura, EvaluacionBase, Evaluacion, AlumnoEvaluacion, 
    Clase, AsignaturaImpartida, Estudiante, AsignaturaInscrita, Curso
)

def mostrar_estadisticas_generales():
    """
    Muestra estadísticas generales del sistema
    """
    print("📊 ESTADÍSTICAS GENERALES DEL SISTEMA")
    print("="*60)
    
    total_asignaturas = Asignatura.objects.exclude(nombre="Ninguna").count()
    total_evaluaciones_base = EvaluacionBase.objects.count()
    total_evaluaciones = Evaluacion.objects.count()
    total_notas = AlumnoEvaluacion.objects.count()
    total_estudiantes = Estudiante.objects.count()
    total_clases = Clase.objects.count()
    total_cursos = Curso.objects.count()
    
    print(f"📚 Asignaturas: {total_asignaturas}")
    print(f"📝 Evaluaciones base: {total_evaluaciones_base}")
    print(f"📋 Evaluaciones reales: {total_evaluaciones}")
    print(f"📊 Notas asignadas: {total_notas}")
    print(f"👥 Estudiantes: {total_estudiantes}")
    print(f"🏫 Clases: {total_clases}")
    print(f"🎓 Cursos: {total_cursos}")
    
    if total_notas > 0:
        promedio_notas = AlumnoEvaluacion.objects.aggregate(
            promedio=models.Avg('nota')
        )['promedio']
        print(f"📊 Promedio general de notas: {promedio_notas:.2f}")
        
        # Estadísticas adicionales
        notas_aprobadas = AlumnoEvaluacion.objects.filter(nota__gte=4.0).count()
        porcentaje_aprobacion = (notas_aprobadas / total_notas) * 100
        print(f"✅ Notas aprobadas: {notas_aprobadas} ({porcentaje_aprobacion:.1f}%)")

def mostrar_evaluaciones_por_asignatura():
    """
    Muestra las evaluaciones base por asignatura
    """
    print("\n📝 EVALUACIONES BASE POR ASIGNATURA")
    print("="*60)
    
    for asignatura in Asignatura.objects.exclude(nombre="Ninguna").order_by('nivel', 'nombre'):
        evaluaciones_base = EvaluacionBase.objects.filter(asignatura=asignatura)
        
        print(f"\n📚 {asignatura.nombre} ({asignatura.nivel}°)")
        for eval_base in evaluaciones_base:
            print(f"   • {eval_base.nombre}: {eval_base.ponderacion}%")

def mostrar_evaluaciones_por_curso():
    """
    Muestra las evaluaciones reales por curso
    """
    print("\n📋 EVALUACIONES REALES POR CURSO")
    print("="*60)
    
    for curso in Curso.objects.all().order_by('nivel', 'letra'):
        clases = Clase.objects.filter(curso=curso)
        
        if clases.exists():
            print(f"\n🎓 {curso}")
            
            for clase in clases:
                asignatura = clase.asignatura_impartida.asignatura
                evaluaciones = Evaluacion.objects.filter(clase=clase)
                
                print(f"   📚 {asignatura.nombre}: {evaluaciones.count()} evaluaciones")
                
                for evaluacion in evaluaciones:
                    fecha_str = evaluacion.fecha.strftime('%d/%m/%Y')
                    print(f"     • {evaluacion.evaluacion_base.nombre} - {fecha_str}")

def mostrar_notas_por_estudiante():
    """
    Muestra un resumen de notas por estudiante
    """
    print("\n📊 RESUMEN DE NOTAS POR ESTUDIANTE")
    print("="*60)
    
    # Mostrar solo los primeros 5 estudiantes como ejemplo
    estudiantes = Estudiante.objects.select_related('usuario', 'curso').all()[:5]
    
    for estudiante in estudiantes:
        notas = AlumnoEvaluacion.objects.filter(estudiante=estudiante)
        
        if notas.exists():
            promedio_estudiante = notas.aggregate(promedio=models.Avg('nota'))['promedio']
            print(f"\n👤 {estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno} ({estudiante.curso})")
            print(f"   📊 Promedio: {promedio_estudiante:.2f}")
            print(f"   📝 Total evaluaciones: {notas.count()}")
            
            # Mostrar las primeras 3 notas como ejemplo
            for nota in notas[:3]:
                evaluacion = nota.evaluacion
                asignatura = evaluacion.evaluacion_base.asignatura
                print(f"     • {asignatura.nombre} - {evaluacion.evaluacion_base.nombre}: {nota.nota}")

def mostrar_estadisticas_por_asignatura():
    """
    Muestra estadísticas de rendimiento por asignatura
    """
    print("\n📈 ESTADÍSTICAS POR ASIGNATURA")
    print("="*60)
    
    for asignatura in Asignatura.objects.exclude(nombre="Ninguna").order_by('nivel', 'nombre'):
        evaluaciones = Evaluacion.objects.filter(evaluacion_base__asignatura=asignatura)
        
        if evaluaciones.exists():
            notas = AlumnoEvaluacion.objects.filter(evaluacion__in=evaluaciones)
            
            if notas.exists():
                promedio = notas.aggregate(promedio=models.Avg('nota'))['promedio']
                total_notas = notas.count()
                notas_aprobadas = notas.filter(nota__gte=4.0).count()
                porcentaje_aprobacion = (notas_aprobadas / total_notas) * 100
                
                print(f"\n📚 {asignatura.nombre} ({asignatura.nivel}°)")
                print(f"   📊 Promedio: {promedio:.2f}")
                print(f"   📝 Total notas: {total_notas}")
                print(f"   ✅ Aprobación: {porcentaje_aprobacion:.1f}%")

def main():
    """
    Función principal que ejecuta todas las verificaciones
    """
    print("🔍 VERIFICACIÓN DEL SISTEMA DE EVALUACIONES")
    print("="*60)
    
    # Verificar que hay datos
    if EvaluacionBase.objects.count() == 0:
        print("❌ No hay evaluaciones base en el sistema")
        return
    
    if Evaluacion.objects.count() == 0:
        print("❌ No hay evaluaciones reales en el sistema")
        return
    
    if AlumnoEvaluacion.objects.count() == 0:
        print("❌ No hay notas asignadas en el sistema")
        return
    
    print("✅ Sistema de evaluaciones poblado correctamente")
    
    # Mostrar estadísticas
    mostrar_estadisticas_generales()
    mostrar_evaluaciones_por_asignatura()
    mostrar_evaluaciones_por_curso()
    mostrar_notas_por_estudiante()
    mostrar_estadisticas_por_asignatura()
    
    print("\n✅ VERIFICACIÓN COMPLETADA")

if __name__ == "__main__":
    main() 