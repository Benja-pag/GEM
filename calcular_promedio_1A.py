import os
import django
import sys
from datetime import date

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Curso, Estudiante, AlumnoEvaluacion
from django.db.models import Avg

def calcular_promedio_1A():
    print("=" * 60)
    print("CÁLCULO DE PROMEDIO GENERAL - CURSO 1°A")
    print("=" * 60)
    
    try:
        # Buscar el curso 1°A
        curso_1a = Curso.objects.get(nivel=1, letra='A')
        print(f"✅ Curso encontrado: {curso_1a.nivel}°{curso_1a.letra}")
        
        # Obtener estudiantes del curso
        estudiantes = curso_1a.estudiantes.all()
        total_estudiantes = estudiantes.count()
        print(f"📊 Total de estudiantes en 1°A: {total_estudiantes}")
        
        if total_estudiantes == 0:
            print("❌ No hay estudiantes en el curso 1°A")
            return
        
        # Período de evaluaciones (todo el año 2025)
        fecha_inicio = date(2025, 1, 1)
        fecha_fin = date(2025, 12, 31)
        print(f"📅 Período de evaluaciones: {fecha_inicio} a {fecha_fin}")
        
        # Calcular promedio de cada estudiante
        promedios_estudiantes = []
        suma_total_notas = 0
        total_evaluaciones_curso = 0
        
        print("\n" + "=" * 60)
        print("DETALLE POR ESTUDIANTE:")
        print("=" * 60)
        
        for i, estudiante in enumerate(estudiantes, 1):
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
                
                # Sumar todas las notas para promedio general
                suma_notas = sum([eval.nota for eval in evaluaciones])
                suma_total_notas += suma_notas
                
                nombre_completo = f"{estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}"
                print(f"{i:2d}. {nombre_completo}")
                print(f"    📝 Evaluaciones: {total_eval_estudiante}")
                print(f"    📊 Promedio: {promedio_estudiante:.2f}")
                print(f"    ➕ Suma notas: {suma_notas:.1f}")
            else:
                nombre_completo = f"{estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}"
                print(f"{i:2d}. {nombre_completo}")
                print(f"    ❌ Sin evaluaciones")
        
        # Cálculos finales
        estudiantes_con_notas = len(promedios_estudiantes)
        
        print("\n" + "=" * 60)
        print("RESUMEN FINAL:")
        print("=" * 60)
        
        if estudiantes_con_notas > 0:
            # Método 1: Promedio de promedios (cada estudiante cuenta igual)
            promedio_de_promedios = sum(promedios_estudiantes) / estudiantes_con_notas
            
            # Método 2: Promedio general (todas las notas cuentan igual)
            promedio_general = suma_total_notas / total_evaluaciones_curso if total_evaluaciones_curso > 0 else 0
            
            print(f"👥 Estudiantes con evaluaciones: {estudiantes_con_notas}/{total_estudiantes}")
            print(f"📝 Total de evaluaciones: {total_evaluaciones_curso}")
            print(f"➕ Suma total de notas: {suma_total_notas:.1f}")
            print()
            print("📊 PROMEDIOS CALCULADOS:")
            print(f"   • Promedio de promedios: {promedio_de_promedios:.2f}")
            print(f"   • Promedio general: {promedio_general:.2f}")
            print()
            
            # Estadísticas adicionales
            promedio_max = max(promedios_estudiantes)
            promedio_min = min(promedios_estudiantes)
            estudiantes_aprobados = len([p for p in promedios_estudiantes if p >= 4.0])
            porcentaje_aprobacion = (estudiantes_aprobados / estudiantes_con_notas) * 100
            
            print("📈 ESTADÍSTICAS ADICIONALES:")
            print(f"   • Promedio más alto: {promedio_max:.2f}")
            print(f"   • Promedio más bajo: {promedio_min:.2f}")
            print(f"   • Estudiantes aprobados: {estudiantes_aprobados}/{estudiantes_con_notas}")
            print(f"   • Porcentaje de aprobación: {porcentaje_aprobacion:.1f}%")
            
        else:
            print("❌ Ningún estudiante tiene evaluaciones registradas")
        
        print("\n" + "=" * 60)
        
    except Curso.DoesNotExist:
        print("❌ Error: No se encontró el curso 1°A")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    calcular_promedio_1A() 