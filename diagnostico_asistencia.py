#!/usr/bin/env python
"""
Script de diagnóstico para revisar el problema con las asignaturas Música y Tecnología
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
    AsignaturaInscrita, Curso, Asignatura
)

def diagnosticar_asistencia():
    """Diagnostica el problema con las asignaturas Música y Tecnología"""
    print("🔍 DIAGNÓSTICO DE ASISTENCIA")
    print("=" * 50)
    
    # 1. Revisar asignaturas existentes
    print("\n1. ASIGNATURAS EN EL SISTEMA:")
    asignaturas = Asignatura.objects.all()
    for asignatura in asignaturas:
        print(f"   - {asignatura.nombre}")
    
    # 2. Buscar específicamente Música y Tecnología
    print("\n2. BUSCANDO MÚSICA Y TECNOLOGÍA:")
    musica = Asignatura.objects.filter(nombre__icontains='música').first()
    tecnologia = Asignatura.objects.filter(nombre__icontains='tecnología').first()
    
    if musica:
        print(f"   ✅ Música encontrada: {musica.nombre}")
    else:
        print("   ❌ Música NO encontrada")
    
    if tecnologia:
        print(f"   ✅ Tecnología encontrada: {tecnologia.nombre}")
    else:
        print("   ❌ Tecnología NO encontrada")
    
    # 3. Revisar asignaturas impartidas
    print("\n3. ASIGNATURAS IMPARTIDAS:")
    asignaturas_impartidas = AsignaturaImpartida.objects.all()
    for ai in asignaturas_impartidas:
        print(f"   - {ai.asignatura.nombre} (Docente: {ai.docente.usuario.nombre})")
    
    # 4. Revisar un estudiante específico
    print("\n4. REVISANDO UN ESTUDIANTE:")
    estudiante = Estudiante.objects.first()
    if estudiante:
        print(f"   Estudiante: {estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}")
        print(f"   Curso: {estudiante.curso}")
        
        # Asignaturas inscritas del estudiante
        print("   Asignaturas inscritas:")
        asignaturas_inscritas = AsignaturaInscrita.objects.filter(estudiante=estudiante)
        for ai in asignaturas_inscritas:
            print(f"     - {ai.asignatura_impartida.asignatura.nombre}")
        
        # Asistencia del estudiante
        print("   Registros de asistencia:")
        asistencias = Asistencia.objects.filter(estudiante=estudiante)
        print(f"     Total registros: {asistencias.count()}")
        
        # Agrupar por asignatura
        from django.db.models import Count
        asistencia_por_asignatura = asistencias.values(
            'clase__asignatura_impartida__asignatura__nombre'
        ).annotate(
            total=Count('id'),
            presentes=Count('id', filter={'estado': 'presente'}),
            ausentes=Count('id', filter={'estado': 'ausente'}),
            justificados=Count('id', filter={'estado': 'justificado'})
        )
        
        for item in asistencia_por_asignatura:
            nombre = item['clase__asignatura_impartida__asignatura__nombre']
            total = item['total']
            presentes = item['presentes']
            ausentes = item['ausentes']
            justificados = item['justificados']
            porcentaje = (presentes / total * 100) if total > 0 else 0
            
            print(f"     {nombre}: {porcentaje:.1f}% ({presentes}/{total})")
        
        # Verificar específicamente Música y Tecnología
        print("\n   Verificando Música y Tecnología:")
        musica_asistencias = asistencias.filter(clase__asignatura_impartida__asignatura__nombre='Música')
        tecnologia_asistencias = asistencias.filter(clase__asignatura_impartida__asignatura__nombre='Tecnología')
        
        print(f"     Música: {musica_asistencias.count()} registros")
        print(f"     Tecnología: {tecnologia_asistencias.count()} registros")
    
    # 5. Revisar fechas de asistencia
    print("\n5. FECHAS DE ASISTENCIA:")
    fechas_unicas = asistencias.values_list('fecha', flat=True).distinct().order_by('fecha')
    print(f"   Fechas con registros: {len(fechas_unicas)}")
    for fecha in fechas_unicas[:5]:
        print(f"     - {fecha}")
    
    # 6. Verificar el mes actual
    print("\n6. MES ACTUAL:")
    hoy = date.today()
    primer_dia = date(hoy.year, hoy.month, 1)
    print(f"   Mes actual: {hoy.month}/{hoy.year}")
    print(f"   Primer día del mes: {primer_dia}")
    
    # Asistencia del mes actual
    asistencia_mes = asistencias.filter(fecha__gte=primer_dia)
    print(f"   Registros del mes actual: {asistencia_mes.count()}")

if __name__ == "__main__":
    diagnosticar_asistencia() 