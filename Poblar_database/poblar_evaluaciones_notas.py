import os
import django
import sys
import random
from datetime import date, timedelta
from django.db import models

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import (
    Asignatura, EvaluacionBase, Evaluacion, AlumnoEvaluacion, 
    Clase, AsignaturaImpartida, Estudiante, AsignaturaInscrita
)

def limpiar_evaluaciones_anteriores():
    """
    Limpia todas las evaluaciones y notas anteriores
    """
    print("🧹 Limpiando evaluaciones y notas anteriores...")
    
    # Eliminar en orden para respetar las foreign keys
    notas_eliminadas = AlumnoEvaluacion.objects.all().delete()
    evaluaciones_eliminadas = Evaluacion.objects.all().delete()
    
    print(f"✅ Se eliminaron {notas_eliminadas[0]} notas anteriores")
    print(f"✅ Se eliminaron {evaluaciones_eliminadas[0]} evaluaciones anteriores")

def crear_evaluaciones_base():
    """
    Crea 3 evaluaciones base por asignatura con ponderación de 40%
    """
    print("\n📝 CREANDO EVALUACIONES BASE")
    print("="*50)
    
    evaluaciones_base_creadas = 0
    
    for asignatura in Asignatura.objects.all():
        if asignatura.nombre == "Ninguna":
            continue
            
        print(f"\n📚 Asignatura: {asignatura.nombre} ({asignatura.nivel}°)")
        
        # Crear 3 evaluaciones base por asignatura
        evaluaciones_base = [
            ("Prueba 1", 40.0, "Primera prueba parcial del semestre"),
            ("Prueba 2", 40.0, "Segunda prueba parcial del semestre"),
            ("Prueba 3", 40.0, "Tercera prueba parcial del semestre"),
        ]
        
        for nombre, ponderacion, descripcion in evaluaciones_base:
            evaluacion_base, created = EvaluacionBase.objects.get_or_create(
                asignatura=asignatura,
                nombre=nombre,
                defaults={
                    'ponderacion': ponderacion,
                    'descripcion': descripcion
                }
            )
            
            if created:
                evaluaciones_base_creadas += 1
                print(f"   ✅ Creada: {nombre} ({ponderacion}%)")
            else:
                print(f"   ⚠️ Ya existía: {nombre}")
    
    print(f"\n🎯 Total evaluaciones base creadas: {evaluaciones_base_creadas}")
    return evaluaciones_base_creadas

def crear_evaluaciones_reales():
    """
    Crea evaluaciones reales para cada clase basadas en las evaluaciones base
    """
    print("\n📋 CREANDO EVALUACIONES REALES")
    print("="*50)
    
    evaluaciones_creadas = 0
    
    # Obtener todas las clases que tienen asignaturas impartidas
    clases = Clase.objects.select_related('asignatura_impartida__asignatura', 'curso').all()
    
    for clase in clases:
        asignatura = clase.asignatura_impartida.asignatura
        curso = clase.curso
        
        print(f"\n🎯 Clase: {asignatura.nombre} - {curso}")
        
        # Obtener las evaluaciones base de esta asignatura
        evaluaciones_base = EvaluacionBase.objects.filter(asignatura=asignatura)
        
        if not evaluaciones_base.exists():
            print(f"   ⚠️ No hay evaluaciones base para {asignatura.nombre}")
            continue
        
        # Crear una evaluación real para cada evaluación base
        for i, evaluacion_base in enumerate(evaluaciones_base):
            # Generar fechas distribuidas a lo largo del semestre
            fecha_base = date(2024, 3, 1)  # Inicio del semestre
            fecha_evaluacion = fecha_base + timedelta(days=30 * (i + 1))  # Cada mes
            
            evaluacion, created = Evaluacion.objects.get_or_create(
                evaluacion_base=evaluacion_base,
                clase=clase,
                defaults={
                    'fecha': fecha_evaluacion,
                    'observaciones': f"{evaluacion_base.nombre} aplicada en {curso}"
                }
            )
            
            if created:
                evaluaciones_creadas += 1
                print(f"   ✅ Creada: {evaluacion_base.nombre} - {fecha_evaluacion.strftime('%d/%m/%Y')}")
            else:
                print(f"   ⚠️ Ya existía: {evaluacion_base.nombre}")
    
    print(f"\n🎯 Total evaluaciones reales creadas: {evaluaciones_creadas}")
    return evaluaciones_creadas

def asignar_notas_estudiantes():
    """
    Asigna notas distintas a cada estudiante en cada evaluación
    """
    print("\n📊 ASIGNANDO NOTAS A ESTUDIANTES")
    print("="*50)
    
    notas_creadas = 0
    estudiantes_procesados = 0
    
    # Obtener todas las evaluaciones
    evaluaciones = Evaluacion.objects.select_related(
        'evaluacion_base__asignatura', 
        'clase__asignatura_impartida__asignatura',
        'clase__curso'
    ).all()
    
    for evaluacion in evaluaciones:
        clase = evaluacion.clase
        curso = clase.curso
        asignatura = evaluacion.evaluacion_base.asignatura
        
        print(f"\n📝 Evaluación: {evaluacion.evaluacion_base.nombre} - {asignatura.nombre} - {curso}")
        
        # Obtener estudiantes inscritos en esta asignatura impartida
        estudiantes_inscritos = Estudiante.objects.filter(
            asignaturas_inscritas__asignatura_impartida=clase.asignatura_impartida,
            curso=curso
        ).select_related('usuario')
        
        if not estudiantes_inscritos.exists():
            print(f"   ⚠️ No hay estudiantes inscritos en {asignatura.nombre} - {curso}")
            continue
        
        print(f"   👥 Estudiantes a calificar: {estudiantes_inscritos.count()}")
        
        # Asignar notas distintas a cada estudiante
        notas_disponibles = [3.0, 3.2, 3.5, 3.8, 4.0, 4.2, 4.5, 4.8, 5.0, 5.2, 5.5, 5.8, 6.0, 6.2, 6.5, 6.8, 7.0]
        random.shuffle(notas_disponibles)
        
        for i, estudiante in enumerate(estudiantes_inscritos):
            # Usar notas distintas para cada estudiante
            nota = notas_disponibles[i % len(notas_disponibles)]
            
            # Agregar pequeña variación para evitar notas idénticas
            variacion = random.uniform(-0.3, 0.3)
            nota_final = max(1.0, min(7.0, nota + variacion))
            nota_final = round(nota_final, 1)
            
            # Crear la nota del estudiante
            alumno_evaluacion, created = AlumnoEvaluacion.objects.get_or_create(
                estudiante=estudiante,
                evaluacion=evaluacion,
                defaults={
                    'nota': nota_final,
                    'observaciones': f"Nota asignada automáticamente"
                }
            )
            
            if created:
                notas_creadas += 1
                print(f"     ✅ {estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}: {nota_final}")
            else:
                print(f"     ⚠️ Ya tenía nota: {estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}")
        
        estudiantes_procesados += estudiantes_inscritos.count()
    
    print(f"\n🎯 Total notas creadas: {notas_creadas}")
    print(f"🎯 Total estudiantes procesados: {estudiantes_procesados}")
    return notas_creadas, estudiantes_procesados

def mostrar_estadisticas():
    """
    Muestra estadísticas del sistema de evaluaciones
    """
    print("\n📈 ESTADÍSTICAS DEL SISTEMA")
    print("="*50)
    
    total_asignaturas = Asignatura.objects.exclude(nombre="Ninguna").count()
    total_evaluaciones_base = EvaluacionBase.objects.count()
    total_evaluaciones = Evaluacion.objects.count()
    total_notas = AlumnoEvaluacion.objects.count()
    total_estudiantes = Estudiante.objects.count()
    total_clases = Clase.objects.count()
    
    print(f"📚 Asignaturas: {total_asignaturas}")
    print(f"📝 Evaluaciones base: {total_evaluaciones_base}")
    print(f"📋 Evaluaciones reales: {total_evaluaciones}")
    print(f"📊 Notas asignadas: {total_notas}")
    print(f"👥 Estudiantes: {total_estudiantes}")
    print(f"🏫 Clases: {total_clases}")
    
    if total_notas > 0 and total_estudiantes > 0:
        promedio_notas = AlumnoEvaluacion.objects.aggregate(
            promedio=models.Avg('nota')
        )['promedio']
        print(f"📊 Promedio general de notas: {promedio_notas:.2f}")

def main():
    """
    Función principal que ejecuta todo el proceso
    """
    print("🚀 POBLADO DE EVALUACIONES Y NOTAS")
    print("="*60)
    
    # Limpiar datos anteriores
    limpiar_evaluaciones_anteriores()
    
    # Crear evaluaciones base
    evaluaciones_base_creadas = crear_evaluaciones_base()
    
    # Crear evaluaciones reales
    evaluaciones_creadas = crear_evaluaciones_reales()
    
    # Asignar notas
    notas_creadas, estudiantes_procesados = asignar_notas_estudiantes()
    
    # Mostrar estadísticas
    mostrar_estadisticas()
    
    print("\n✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("="*60)
    print(f"📝 Evaluaciones base creadas: {evaluaciones_base_creadas}")
    print(f"📋 Evaluaciones reales creadas: {evaluaciones_creadas}")
    print(f"📊 Notas asignadas: {notas_creadas}")
    print(f"👥 Estudiantes procesados: {estudiantes_procesados}")

if __name__ == "__main__":
    main() 