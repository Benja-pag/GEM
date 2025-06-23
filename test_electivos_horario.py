#!/usr/bin/env python
"""
Script de prueba para verificar que los electivos se guarden correctamente en el horario
"""

import os
import sys
import django

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import AsignaturaInscrita, Clase, Asignatura, Estudiante, AsignaturaImpartida
from Core.views.alumnos import get_horario_estudiante

def test_electivos_horario():
    """Prueba que los electivos aparezcan correctamente en el horario"""
    print("🧪 PRUEBA: Verificar que los electivos aparezcan en el horario")
    print("=" * 60)
    
    # 1. Verificar que hay electivos en la base de datos
    print("\n1. Verificando electivos disponibles...")
    electivos = Asignatura.objects.filter(es_electivo=True)
    print(f"   📚 Total de electivos: {electivos.count()}")
    
    for electivo in electivos:
        print(f"   • {electivo.nombre} ({electivo.nivel}° medio)")
    
    # 2. Verificar que hay clases programadas para electivos
    print("\n2. Verificando clases de electivos...")
    clases_electivos = Clase.objects.filter(
        asignatura_impartida__asignatura__es_electivo=True
    ).select_related(
        'asignatura_impartida__asignatura',
        'asignatura_impartida__docente__usuario'
    )
    
    print(f"   📅 Total de clases de electivos: {clases_electivos.count()}")
    
    for clase in clases_electivos:
        docente = clase.asignatura_impartida.docente.usuario
        print(f"   • {clase.asignatura_impartida.asignatura.nombre} - {clase.fecha} bloque {clase.horario} - Prof. {docente.nombre} {docente.apellido_paterno}")
    
    # 3. Verificar estudiantes con electivos inscritos
    print("\n3. Verificando estudiantes con electivos inscritos...")
    estudiantes_con_electivos = Estudiante.objects.filter(
        asignaturas_inscritas__asignatura_impartida__asignatura__es_electivo=True,
        asignaturas_inscritas__validada=True
    ).distinct()
    
    print(f"   👥 Estudiantes con electivos inscritos: {estudiantes_con_electivos.count()}")
    
    # 4. Probar con un estudiante específico
    if estudiantes_con_electivos.exists():
        estudiante = estudiantes_con_electivos.first()
        print(f"\n4. Probando horario del estudiante: {estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}")
        
        # Obtener electivos inscritos
        electivos_inscritos = AsignaturaInscrita.objects.filter(
            estudiante=estudiante,
            asignatura_impartida__asignatura__es_electivo=True,
            validada=True
        ).select_related(
            'asignatura_impartida__asignatura',
            'asignatura_impartida__docente__usuario'
        )
        
        print(f"   📚 Electivos inscritos: {electivos_inscritos.count()}")
        for inscripcion in electivos_inscritos:
            print(f"   • {inscripcion.asignatura_impartida.asignatura.nombre}")
        
        # Obtener horario del estudiante
        horario = get_horario_estudiante(estudiante.pk)
        
        print(f"\n5. Horario del estudiante:")
        dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
        bloques_electivos = ['7', '8', '9']
        
        for dia in dias:
            print(f"\n   📅 {dia}:")
            for bloque in bloques_electivos:
                if horario[dia][bloque]:
                    clase_info = horario[dia][bloque]
                    print(f"      • Bloque {bloque}: {clase_info['asignatura']} - {clase_info['docente']} - {clase_info['sala']}")
                else:
                    print(f"      • Bloque {bloque}: Vacío")
        
        # Verificar que los electivos aparecen en el horario
        electivos_en_horario = 0
        for dia in dias:
            for bloque in bloques_electivos:
                if horario[dia][bloque]:
                    electivos_en_horario += 1
        
        print(f"\n6. Resultado:")
        print(f"   ✅ Electivos inscritos: {electivos_inscritos.count()}")
        print(f"   ✅ Electivos en horario: {electivos_en_horario}")
        
        if electivos_inscritos.count() == electivos_en_horario:
            print("   🎉 ¡ÉXITO! Los electivos aparecen correctamente en el horario")
        else:
            print("   ❌ PROBLEMA: Los electivos no aparecen correctamente en el horario")
            
    else:
        print("   ⚠️ No hay estudiantes con electivos inscritos para probar")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_electivos_horario() 