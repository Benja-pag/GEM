#!/usr/bin/env python
"""
Script para poblar datos de asistencia del mes actual
Basado en las clases existentes en el sistema
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
import random

# Agrega el directorio raíz del proyecto al path (sube dos niveles desde subcarpeta)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import (
    Clase, Asistencia, Estudiante, AsignaturaInscrita, 
    AsignaturaImpartida, Curso
)
from django.utils import timezone

def obtener_fechas_mes_actual():
    """Obtiene todas las fechas de junio que son días de semana"""
    # Usar junio de 2025 específicamente
    primer_dia = date(2025, 6, 1)
    ultimo_dia = date(2025, 6, 30)
    
    fechas = []
    fecha_actual = primer_dia
    
    while fecha_actual <= ultimo_dia:
        # Solo incluir días de semana (0=Lunes, 6=Domingo)
        if fecha_actual.weekday() < 5:  # Lunes a Viernes
            fechas.append(fecha_actual)
        fecha_actual += timedelta(days=1)
    
    return fechas

def mapear_dia_semana(fecha):
    """Mapea una fecha a los días de la semana del modelo"""
    dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
    return dias[fecha.weekday()]

def poblar_asistencia_mes():
    """Pobla datos de asistencia para junio"""
    print("🎯 Iniciando poblamiento de asistencia de junio 2025...")
    
    # Eliminar todas las asistencias existentes
    print("🗑️ Eliminando asistencias existentes...")
    Asistencia.objects.all().delete()
    
    # Obtener fechas del mes
    fechas_mes = obtener_fechas_mes_actual()
    print(f"📅 Fechas a procesar: {len(fechas_mes)} días de junio")
    for fecha in fechas_mes[:5]:  # Mostrar primeras 5 fechas
        print(f"  - {fecha.strftime('%d/%m/%Y')} ({mapear_dia_semana(fecha)})")
    if len(fechas_mes) > 5:
        print(f"  ... y {len(fechas_mes) - 5} días más")
    
    # Obtener todas las clases existentes
    clases_existentes = Clase.objects.all()
    print(f"📚 Total de clases en el sistema: {clases_existentes.count()}")
    
    # Contadores
    total_registros_creados = 0
    total_registros_existentes = 0
    
    # Lista para bulk create
    asistencias_a_crear = []
    
    # Procesar cada fecha del mes
    for fecha in fechas_mes:
        dia_semana = mapear_dia_semana(fecha)
        
        # Obtener clases para este día de la semana
        clases_dia = clases_existentes.filter(fecha=dia_semana)
        
        if not clases_dia.exists():
            continue
        
        print(f"\n📅 Procesando {fecha.strftime('%d/%m/%Y')} ({dia_semana}): {clases_dia.count()} clases")
        
        for clase in clases_dia:
            # Obtener estudiantes inscritos en esta asignatura
            estudiantes_inscritos = Estudiante.objects.filter(
                asignaturas_inscritas__asignatura_impartida=clase.asignatura_impartida,
                asignaturas_inscritas__validada=True
            ).select_related('usuario')
            
            if not estudiantes_inscritos.exists():
                continue
            
            print(f"  📖 {clase.asignatura_impartida.asignatura.nombre} - {clase.curso}: {estudiantes_inscritos.count()} estudiantes")
            
            # Crear registros de asistencia para cada estudiante
            for estudiante in estudiantes_inscritos:
                # Generar datos de asistencia aleatorios pero realistas
                # 85% de probabilidad de estar presente
                presente = random.random() < 0.85
                justificado = False
                observaciones = ""
                
                # Si está ausente, 30% de probabilidad de estar justificado
                if not presente and random.random() < 0.30:
                    justificado = True
                    observaciones = random.choice([
                        "Médico",
                        "Familiar",
                        "Actividad escolar",
                        "Cita médica",
                        "Problema familiar"
                    ])
                
                # Crear el registro de asistencia con la fecha específica
                fecha_registro = timezone.make_aware(datetime.combine(fecha, datetime.min.time()))
                
                asistencias_a_crear.append(
                    Asistencia(
                        clase=clase,
                        estudiante=estudiante,
                        presente=presente,
                        justificado=justificado,
                        observaciones=observaciones,
                        fecha_registro=fecha_registro
                    )
                )
                
                total_registros_creados += 1
                
                # Hacer bulk create cada 1000 registros para no sobrecargar la memoria
                if len(asistencias_a_crear) >= 1000:
                    try:
                        Asistencia.objects.bulk_create(asistencias_a_crear, batch_size=1000, ignore_conflicts=True)
                        print(f"  ✅ Creados {len(asistencias_a_crear)} registros")
                        asistencias_a_crear = []
                    except Exception as e:
                        print(f"  ❌ Error al crear registros: {str(e)}")
    
    # Crear los registros restantes
    if asistencias_a_crear:
        try:
            Asistencia.objects.bulk_create(asistencias_a_crear, batch_size=1000, ignore_conflicts=True)
            print(f"  ✅ Creados {len(asistencias_a_crear)} registros finales")
        except Exception as e:
            print(f"  ❌ Error al crear registros finales: {str(e)}")
    
    print(f"\n✅ Poblamiento completado!")
    print(f"📊 Resumen:")
    print(f"   - Registros creados: {total_registros_creados}")
    print(f"   - Registros existentes (omitidos): {total_registros_existentes}")
    print(f"   - Total procesados: {total_registros_creados + total_registros_existentes}")
    
    # Mostrar estadísticas
    mostrar_estadisticas_asistencia()

def mostrar_estadisticas_asistencia():
    """Muestra estadísticas de asistencia del mes actual"""
    print("\n📈 Estadísticas de Asistencia del Mes Actual:")
    
    # Obtener fechas del mes
    fechas_mes = obtener_fechas_mes_actual()
    
    # Obtener todas las asistencias del mes
    asistencias_mes = Asistencia.objects.filter(
        fecha_registro__date__in=fechas_mes
    )
    
    total_asistencias = asistencias_mes.count()
    total_presentes = asistencias_mes.filter(presente=True).count()
    total_ausentes = asistencias_mes.filter(presente=False).count()
    total_justificados = asistencias_mes.filter(justificado=True).count()
    
    if total_asistencias > 0:
        porcentaje_asistencia = (total_presentes / total_asistencias) * 100
        porcentaje_justificados = (total_justificados / total_ausentes) * 100 if total_ausentes > 0 else 0
        
        print(f"   - Total de registros: {total_asistencias}")
        print(f"   - Presentes: {total_presentes} ({porcentaje_asistencia:.1f}%)")
        print(f"   - Ausentes: {total_ausentes} ({100-porcentaje_asistencia:.1f}%)")
        print(f"   - Justificados: {total_justificados} ({porcentaje_justificados:.1f}% de ausencias)")
    
    # Estadísticas por curso
    print(f"\n📊 Estadísticas por Curso:")
    cursos = Curso.objects.all().order_by('nivel', 'letra')
    
    for curso in cursos:
        asistencias_curso = asistencias_mes.filter(
            clase__curso=curso
        )
        
        if asistencias_curso.exists():
            total_curso = asistencias_curso.count()
            presentes_curso = asistencias_curso.filter(presente=True).count()
            porcentaje_curso = (presentes_curso / total_curso) * 100
            
            print(f"   - {curso}: {presentes_curso}/{total_curso} ({porcentaje_curso:.1f}%)")

if __name__ == "__main__":
    try:
        # Poblar asistencia
        poblar_asistencia_mes()
        
        print("\n🎉 ¡Proceso completado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante el proceso: {e}")
        import traceback
        traceback.print_exc() 