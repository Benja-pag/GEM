#!/usr/bin/env python
"""
Script para verificar que los electivos se hayan creado correctamente
Verifica asignaturas electivas, docentes asignados y horarios
"""

import os
import sys
import django

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Asignatura, AsignaturaImpartida, Clase

def verificar_electivos():
    """Verifica que los electivos se hayan creado correctamente"""
    print("🔍 VERIFICANDO ELECTIVOS")
    print("=" * 50)
    
    # Verificar asignaturas electivas
    electivos = Asignatura.objects.filter(es_electivo=True).order_by('nivel', 'nombre')
    
    if not electivos.exists():
        print("❌ No se encontraron asignaturas electivas")
        return
    
    print(f"📚 Total de asignaturas electivas: {electivos.count()}")
    
    # Agrupar por nivel
    electivos_por_nivel = {}
    for electivo in electivos:
        if electivo.nivel not in electivos_por_nivel:
            electivos_por_nivel[electivo.nivel] = []
        electivos_por_nivel[electivo.nivel].append(electivo)
    
    for nivel, electivos_nivel in electivos_por_nivel.items():
        print(f"\n🎓 {nivel}° Medio ({len(electivos_nivel)} electivos):")
        for electivo in electivos_nivel:
            print(f"  • {electivo.nombre}")
    
    # Verificar asignaturas impartidas
    print(f"\n📝 VERIFICANDO ASIGNATURAS IMPARTIDAS:")
    print("-" * 40)
    
    impartidas = AsignaturaImpartida.objects.filter(
        asignatura__es_electivo=True
    ).select_related('asignatura', 'docente__usuario', 'docente__especialidad')
    
    if not impartidas.exists():
        print("❌ No se encontraron asignaturas electivas impartidas")
        return
    
    print(f"📊 Total de electivos impartidos: {impartidas.count()}")
    
    for impartida in impartidas:
        docente_info = f"{impartida.docente.usuario.nombre} {impartida.docente.usuario.apellido_paterno}"
        especialidad = impartida.docente.especialidad.nombre if impartida.docente.especialidad else "Sin especialidad"
        print(f"  ✅ {impartida.asignatura.nombre} - Prof. {docente_info} ({especialidad}) - Código: {impartida.codigo}")
    
    # Verificar horarios
    print(f"\n🗓️ VERIFICANDO HORARIOS DE ELECTIVOS:")
    print("-" * 40)
    
    clases_electivos = Clase.objects.filter(
        asignatura_impartida__asignatura__es_electivo=True
    ).select_related(
        'asignatura_impartida__asignatura',
        'asignatura_impartida__docente__usuario'
    ).order_by('fecha', 'horario')
    
    if not clases_electivos.exists():
        print("❌ No se encontraron horarios para electivos")
        return
    
    print(f"📅 Total de clases de electivos: {clases_electivos.count()}")
    
    # Agrupar por día
    clases_por_dia = {}
    for clase in clases_electivos:
        if clase.fecha not in clases_por_dia:
            clases_por_dia[clase.fecha] = []
        clases_por_dia[clase.fecha].append(clase)
    
    for dia, clases in clases_por_dia.items():
        print(f"\n📅 {dia}:")
        for clase in clases:
            docente = clase.asignatura_impartida.docente.usuario
            print(f"  • Bloque {clase.horario}: {clase.asignatura_impartida.asignatura.nombre} - Prof. {docente.nombre} {docente.apellido_paterno} - Sala {clase.sala}")
    
    print(f"\n✅ Verificación de electivos completada")
    print(f"📊 Resumen:")
    print(f"   • Asignaturas electivas: {electivos.count()}")
    print(f"   • Electivos impartidos: {impartidas.count()}")
    print(f"   • Clases programadas: {clases_electivos.count()}")

if __name__ == "__main__":
    verificar_electivos() 