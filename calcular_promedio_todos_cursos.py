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

def calcular_promedio_todos_cursos():
    print("=" * 80)
    print("CÁLCULO DE PROMEDIO GENERAL - TODOS LOS CURSOS")
    print("=" * 80)
    
    try:
        # Obtener todos los cursos
        cursos = Curso.objects.all().order_by('nivel', 'letra')
        total_cursos = cursos.count()
        print(f"🏫 Total de cursos encontrados: {total_cursos}")
        
        if total_cursos == 0:
            print("❌ No hay cursos registrados")
            return
        
        # Período de evaluaciones (todo el año 2025)
        fecha_inicio = date(2025, 1, 1)
        fecha_fin = date(2025, 12, 31)
        print(f"📅 Período de evaluaciones: {fecha_inicio} a {fecha_fin}")
        
        # Variables para estadísticas generales
        total_estudiantes_colegio = 0
        total_evaluaciones_colegio = 0
        suma_total_notas_colegio = 0
        promedios_todos_cursos = []
        cursos_data = []
        
        print("\n" + "=" * 80)
        print("DETALLE POR CURSO:")
        print("=" * 80)
        
        for curso in cursos:
            print(f"\n📚 CURSO {curso.nivel}°{curso.letra}")
            print("-" * 40)
            
            # Obtener estudiantes del curso
            estudiantes = curso.estudiantes.all()
            total_estudiantes = estudiantes.count()
            total_estudiantes_colegio += total_estudiantes
            
            print(f"👥 Estudiantes: {total_estudiantes}")
            
            if total_estudiantes == 0:
                print("❌ Curso sin estudiantes")
                cursos_data.append({
                    'curso': f"{curso.nivel}°{curso.letra}",
                    'estudiantes': 0,
                    'evaluaciones': 0,
                    'promedio': 0.0,
                    'aprobados': 0,
                    'porcentaje_aprobacion': 0.0
                })
                continue
            
            # Calcular promedio del curso
            promedios_estudiantes = []
            suma_notas_curso = 0
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
                    
                    # Sumar todas las notas
                    suma_notas = sum([eval.nota for eval in evaluaciones])
                    suma_notas_curso += suma_notas
            
            # Estadísticas del curso
            estudiantes_con_notas = len(promedios_estudiantes)
            total_evaluaciones_colegio += total_evaluaciones_curso
            suma_total_notas_colegio += suma_notas_curso
            
            if estudiantes_con_notas > 0:
                # Promedio del curso (promedio de promedios)
                promedio_curso = sum(promedios_estudiantes) / estudiantes_con_notas
                promedios_todos_cursos.append(promedio_curso)
                
                # Estudiantes aprobados
                estudiantes_aprobados = len([p for p in promedios_estudiantes if p >= 4.0])
                porcentaje_aprobacion = (estudiantes_aprobados / estudiantes_con_notas) * 100
                
                print(f"📝 Evaluaciones: {total_evaluaciones_curso}")
                print(f"📊 Promedio curso: {promedio_curso:.2f}")
                print(f"✅ Aprobados: {estudiantes_aprobados}/{estudiantes_con_notas} ({porcentaje_aprobacion:.1f}%)")
                print(f"📈 Rango: {min(promedios_estudiantes):.2f} - {max(promedios_estudiantes):.2f}")
                
                cursos_data.append({
                    'curso': f"{curso.nivel}°{curso.letra}",
                    'estudiantes': total_estudiantes,
                    'evaluaciones': total_evaluaciones_curso,
                    'promedio': promedio_curso,
                    'aprobados': estudiantes_aprobados,
                    'porcentaje_aprobacion': porcentaje_aprobacion,
                    'promedio_min': min(promedios_estudiantes),
                    'promedio_max': max(promedios_estudiantes)
                })
            else:
                print("❌ Sin evaluaciones registradas")
                cursos_data.append({
                    'curso': f"{curso.nivel}°{curso.letra}",
                    'estudiantes': total_estudiantes,
                    'evaluaciones': 0,
                    'promedio': 0.0,
                    'aprobados': 0,
                    'porcentaje_aprobacion': 0.0
                })
        
        # RESUMEN GENERAL
        print("\n" + "=" * 80)
        print("RESUMEN GENERAL DEL COLEGIO")
        print("=" * 80)
        
        cursos_con_datos = len(promedios_todos_cursos)
        
        if cursos_con_datos > 0:
            # Promedio general del colegio
            promedio_general_colegio = sum(promedios_todos_cursos) / cursos_con_datos
            promedio_ponderado = suma_total_notas_colegio / total_evaluaciones_colegio if total_evaluaciones_colegio > 0 else 0
            
            print(f"🏫 Total estudiantes: {total_estudiantes_colegio}")
            print(f"📚 Cursos con datos: {cursos_con_datos}/{total_cursos}")
            print(f"📝 Total evaluaciones: {total_evaluaciones_colegio}")
            print(f"➕ Suma total notas: {suma_total_notas_colegio:.1f}")
            print()
            print("📊 PROMEDIOS GENERALES:")
            print(f"   • Promedio por cursos: {promedio_general_colegio:.2f}")
            print(f"   • Promedio ponderado: {promedio_ponderado:.2f}")
            print()
            
            # Estadísticas por nivel
            print("📈 ESTADÍSTICAS POR NIVEL:")
            for nivel in [1, 2, 3, 4]:
                cursos_nivel = [c for c in cursos_data if c['curso'].startswith(f"{nivel}°")]
                if cursos_nivel:
                    promedios_nivel = [c['promedio'] for c in cursos_nivel if c['promedio'] > 0]
                    if promedios_nivel:
                        promedio_nivel = sum(promedios_nivel) / len(promedios_nivel)
                        total_est_nivel = sum([c['estudiantes'] for c in cursos_nivel])
                        total_aprob_nivel = sum([c['aprobados'] for c in cursos_nivel])
                        print(f"   • {nivel}° Medio: {promedio_nivel:.2f} ({total_est_nivel} estudiantes, {total_aprob_nivel} aprobados)")
            
            print()
            print("🏆 RANKING DE CURSOS:")
            cursos_ordenados = sorted([c for c in cursos_data if c['promedio'] > 0], 
                                    key=lambda x: x['promedio'], reverse=True)
            
            for i, curso in enumerate(cursos_ordenados, 1):
                print(f"   {i:2d}. {curso['curso']}: {curso['promedio']:.2f} "
                      f"({curso['estudiantes']} est., {curso['porcentaje_aprobacion']:.1f}% aprob.)")
        
        else:
            print("❌ No hay datos de evaluaciones en ningún curso")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    calcular_promedio_todos_cursos() 