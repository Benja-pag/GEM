import os
import django
import sys
from datetime import date

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Curso, Estudiante, AlumnoEvaluacion, Asistencia
from django.db.models import Avg

def mostrar_tabla_completa():
    print("=" * 100)
    print("TABLA COMPLETA DE RENDIMIENTO POR CURSOS")
    print("=" * 100)
    
    # Período de evaluaciones (todo el año 2025)
    fecha_inicio = date(2025, 1, 1)
    fecha_fin = date(2025, 12, 31)
    
    # Encabezado de la tabla
    print(f"{'Curso':<6} {'Estudiantes':<12} {'Evaluaciones':<12} {'Promedio':<10} {'Aprobación':<12} {'Asistencia':<12} {'Estado':<10}")
    print("-" * 100)
    
    try:
        # Obtener todos los cursos
        cursos = Curso.objects.all().order_by('nivel', 'letra')
        
        for curso in cursos:
            # Obtener estudiantes del curso
            estudiantes = curso.estudiantes.all()
            total_estudiantes = estudiantes.count()
            
            if total_estudiantes == 0:
                # Curso sin estudiantes
                print(f"{curso.nivel}°{curso.letra:<4} {0:<12} {0:<12} {0.0:<10.2f} {0.0:<11.1f}% {0.0:<11.1f}% {'N/A':<10}")
                continue
            
            # Calcular datos académicos
            promedios_estudiantes = []
            total_evaluaciones_curso = 0
            
            for estudiante in estudiantes:
                # Obtener evaluaciones del estudiante
                evaluaciones = AlumnoEvaluacion.objects.filter(
                    estudiante=estudiante,
                    evaluacion__fecha__gte=fecha_inicio,
                    evaluacion__fecha__lte=fecha_fin
                )
                
                total_eval_estudiante = evaluaciones.count()
                total_evaluaciones_curso += total_eval_estudiante
                
                if total_eval_estudiante > 0:
                    # Calcular promedio del estudiante
                    promedio_estudiante = evaluaciones.aggregate(promedio=Avg('nota'))['promedio']
                    promedios_estudiantes.append(promedio_estudiante)
            
            # Calcular promedio del curso
            estudiantes_con_notas = len(promedios_estudiantes)
            if estudiantes_con_notas > 0:
                promedio_curso = sum(promedios_estudiantes) / estudiantes_con_notas
                estudiantes_aprobados = len([p for p in promedios_estudiantes if p >= 4.0])
                porcentaje_aprobacion = (estudiantes_aprobados / estudiantes_con_notas) * 100
            else:
                promedio_curso = 0.0
                porcentaje_aprobacion = 0.0
            
            # Calcular asistencia del curso
            asistencias = Asistencia.objects.filter(
                estudiante__curso=curso,
                fecha_registro__date__gte=fecha_inicio,
                fecha_registro__date__lte=fecha_fin
            )
            total_asistencias = asistencias.count()
            presentes = asistencias.filter(presente=True).count()
            porcentaje_asistencia = (presentes / total_asistencias * 100) if total_asistencias > 0 else 0
            
            # Determinar estado basado en asistencia
            if porcentaje_asistencia < 83:
                estado = "Crítico"
            elif porcentaje_asistencia < 85:
                estado = "Regular"
            else:
                estado = "Bueno"
            
            # Mostrar fila de la tabla
            print(f"{curso.nivel}°{curso.letra:<4} {total_estudiantes:<12} {total_evaluaciones_curso:<12} {promedio_curso:<10.2f} {porcentaje_aprobacion:<11.1f}% {porcentaje_asistencia:<11.1f}% {estado:<10}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("-" * 100)
    print("Estados: Crítico (<83% asist.), Regular (83-85% asist.), Bueno (>85% asist.)")
    print("=" * 100)

if __name__ == "__main__":
    mostrar_tabla_completa() 