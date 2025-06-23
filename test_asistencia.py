#!/usr/bin/env python
"""
Script de prueba para verificar que los datos de asistencia se muestran correctamente
"""

import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import (
    Asistencia, Estudiante, AsignaturaImpartida, 
    AsignaturaInscrita, Curso, Docente
)
from Core.views.alumnos import get_asistencia_estudiante
from Core.views.docentes import get_estadisticas_asistencia_docente

def test_asistencia_estudiante():
    """Prueba la función de asistencia de estudiantes"""
    print("🎯 Probando función de asistencia de estudiantes...")
    
    # Obtener un estudiante de prueba
    estudiante = Estudiante.objects.first()
    if not estudiante:
        print("❌ No se encontraron estudiantes en la base de datos")
        return
    
    print(f"📚 Estudiante de prueba: {estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}")
    print(f"📖 Curso: {estudiante.curso}")
    
    # Obtener datos de asistencia
    asistencia = get_asistencia_estudiante(estudiante.pk)
    
    if asistencia:
        print(f"✅ Se encontraron datos de asistencia para {len(asistencia)} asignaturas:")
        for asignatura, datos in asistencia.items():
            print(f"  📖 {asignatura}:")
            print(f"    - Total clases: {datos['total']}")
            print(f"    - Presentes: {datos['presentes']}")
            print(f"    - Ausentes: {datos['ausentes']}")
            print(f"    - Justificados: {datos['justificados']}")
            print(f"    - Porcentaje: {datos['porcentaje']:.1f}%")
    else:
        print("⚠️ No se encontraron datos de asistencia para este estudiante")

def test_asistencia_docente():
    """Prueba la función de asistencia de docentes"""
    print("\n🎯 Probando función de asistencia de docentes...")
    
    # Obtener un docente de prueba
    docente = Docente.objects.first()
    if not docente:
        print("❌ No se encontraron docentes en la base de datos")
        return
    
    print(f"👨‍🏫 Docente de prueba: {docente.usuario.nombre} {docente.usuario.apellido_paterno}")
    
    # Obtener estadísticas de asistencia
    estadisticas = get_estadisticas_asistencia_docente(docente.pk)
    
    if estadisticas:
        print(f"✅ Se encontraron estadísticas de asistencia para {len(estadisticas)} asignaturas/cursos:")
        for clave, datos in estadisticas.items():
            print(f"  📖 {datos['asignatura']} - {datos['curso']}:")
            print(f"    - Total registros: {datos['total']}")
            print(f"    - Presentes: {datos['presentes']}")
            print(f"    - Ausentes: {datos['ausentes']}")
            print(f"    - Justificados: {datos['justificados']}")
            print(f"    - Porcentaje: {datos['porcentaje']:.1f}%")
    else:
        print("⚠️ No se encontraron estadísticas de asistencia para este docente")

def mostrar_estadisticas_generales():
    """Muestra estadísticas generales de asistencia"""
    print("\n📊 Estadísticas Generales de Asistencia:")
    
    # Obtener fechas del mes actual
    hoy = date.today()
    primer_dia = date(hoy.year, hoy.month, 1)
    
    # Si estamos en el primer día del mes, usar el mes anterior
    if hoy.day <= 5:
        primer_dia = primer_dia - timedelta(days=30)
        primer_dia = date(primer_dia.year, primer_dia.month, 1)
    
    # Obtener el último día del mes
    if primer_dia.month == 12:
        ultimo_dia = date(primer_dia.year + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(primer_dia.year, primer_dia.month + 1, 1) - timedelta(days=1)
    
    # Obtener todas las asistencias del mes
    asistencias = Asistencia.objects.filter(
        fecha_registro__date__gte=primer_dia,
        fecha_registro__date__lte=ultimo_dia
    )
    
    total_asistencias = asistencias.count()
    total_presentes = asistencias.filter(presente=True).count()
    total_ausentes = asistencias.filter(presente=False).count()
    total_justificados = asistencias.filter(justificado=True).count()
    
    if total_asistencias > 0:
        porcentaje_asistencia = (total_presentes / total_asistencias) * 100
        porcentaje_justificados = (total_justificados / total_ausentes) * 100 if total_ausentes > 0 else 0
        
        print(f"📅 Período: {primer_dia.strftime('%d/%m/%Y')} - {ultimo_dia.strftime('%d/%m/%Y')}")
        print(f"📊 Total de registros: {total_asistencias}")
        print(f"✅ Presentes: {total_presentes} ({porcentaje_asistencia:.1f}%)")
        print(f"❌ Ausentes: {total_ausentes} ({100-porcentaje_asistencia:.1f}%)")
        print(f"📝 Justificados: {total_justificados} ({porcentaje_justificados:.1f}% de ausencias)")
        
        # Estadísticas por curso
        print(f"\n📚 Estadísticas por Curso:")
        cursos = Curso.objects.all().order_by('nivel', 'letra')
        
        for curso in cursos:
            asistencias_curso = asistencias.filter(clase__curso=curso)
            if asistencias_curso.exists():
                total_curso = asistencias_curso.count()
                presentes_curso = asistencias_curso.filter(presente=True).count()
                porcentaje_curso = (presentes_curso / total_curso) * 100
                
                print(f"  - {curso}: {presentes_curso}/{total_curso} ({porcentaje_curso:.1f}%)")
    else:
        print("⚠️ No hay datos de asistencia para el mes actual")

if __name__ == "__main__":
    try:
        print("🚀 Iniciando pruebas de asistencia...")
        
        # Mostrar estadísticas generales
        mostrar_estadisticas_generales()
        
        # Probar función de estudiantes
        test_asistencia_estudiante()
        
        # Probar función de docentes
        test_asistencia_docente()
        
        print("\n🎉 ¡Pruebas completadas exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc() 