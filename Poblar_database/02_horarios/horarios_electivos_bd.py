#!/usr/bin/env python
"""
Script para poblar horarios de asignaturas electivas
Crea horarios para electivos en bloques de tarde (7, 8, 9) sin conflictos
"""

import os
import sys
import django
import random
from datetime import date, time

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import AsignaturaImpartida, Clase, Asignatura

def poblar_horarios_electivos():
    """Pobla horarios para asignaturas electivas"""
    print("🧹 Limpiando horarios de electivos anteriores...")
    # Eliminar solo las clases de electivos
    Clase.objects.filter(asignatura_impartida__asignatura__es_electivo=True).delete()
    
    print("📚 Obteniendo electivos con profesor asignado...")
    electivos_impartidos = AsignaturaImpartida.objects.filter(
        asignatura__es_electivo=True
    ).select_related('asignatura', 'docente__usuario')
    
    if not electivos_impartidos.exists():
        print("⚠️ No hay asignaturas electivas impartidas para crear horarios.")
        return
    
    # Configuración de horarios para electivos
    dias_semana = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES']  # Viernes tarde libre
    bloques_tarde = ['7', '8', '9']  # Bloques de tarde
    salas_disponibles = ['SALA_1', 'SALA_2', 'SALA_3', 'SALA_4', 'SALA_5', 'SALA_6', 'SALA_7', 'SALA_8']
    
    # Distribuir electivos por días para evitar conflictos
    electivos_por_dia = {}
    for i, impartida in enumerate(electivos_impartidos):
        dia_asignado = dias_semana[i % len(dias_semana)]
        if dia_asignado not in electivos_por_dia:
            electivos_por_dia[dia_asignado] = []
        electivos_por_dia[dia_asignado].append(impartida)
    
    print("🗓️ Creando horarios para electivos...")
    horarios_creados = 0
    
    for dia, impartidas_dia in electivos_por_dia.items():
        print(f"\n📅 Asignando electivos para el {dia}:")
        
        # Horarios y salas ya usados en este día
        horarios_usados = set() # Por ejemplo: "7", "8", "9"
        
        for impartida in impartidas_dia:
            # Los electivos son de 3 bloques, así que siempre ocupan 7, 8, 9
            # Esta lógica asume que el script `electivos_bd.py` se asegura
            # de que no haya más de un electivo por día y nivel.
            
            # Asignar sala aleatoria (la misma para los 3 bloques)
            sala = random.choice(salas_disponibles)
            
            # Crear las 3 clases para el electivo
            for bloque in bloques_tarde:
                Clase.objects.create(
                    asignatura_impartida=impartida,
                    curso=None,  # Los electivos no tienen curso específico
                    fecha=dia,
                    horario=bloque,
                    sala=sala
                )
            
            horarios_creados += 3
            print(f"  ✅ {impartida.asignatura.nombre} - Bloques 7, 8, 9 - Sala {sala} - Prof. {impartida.docente.usuario.nombre} {impartida.docente.usuario.apellido_paterno}")

    print(f"\n🎉 ¡Proceso completado!")
    print(f"📊 Total de clases de electivos creadas: {horarios_creados}")
    print(f"📚 Total de asignaturas electivas con horario: {electivos_impartidos.count()}")

if __name__ == '__main__':
    poblar_horarios_electivos() 