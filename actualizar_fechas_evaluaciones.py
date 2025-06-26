#!/usr/bin/env python
"""
Script para actualizar las fechas de evaluaciones de 2024 a 2025
"""
import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Evaluacion

def actualizar_fechas_evaluaciones():
    """Actualiza todas las fechas de evaluaciones de 2024 a 2025"""
    
    print("🔄 Iniciando actualización de fechas de evaluaciones...")
    
    # Obtener todas las evaluaciones
    evaluaciones = Evaluacion.objects.all()
    total = evaluaciones.count()
    
    print(f"📊 Total de evaluaciones encontradas: {total}")
    
    if total == 0:
        print("❌ No hay evaluaciones para actualizar")
        return
    
    # Mostrar rango actual de fechas
    primera_eval = evaluaciones.first()
    ultima_eval = evaluaciones.last()
    print(f"📅 Rango actual: {primera_eval.fecha} a {ultima_eval.fecha}")
    
    # Actualizar fechas
    actualizadas = 0
    errores = 0
    
    for eval in evaluaciones:
        try:
            fecha_original = eval.fecha
            
            # Cambiar solo el año a 2025, mantener mes y día
            nueva_fecha = date(2025, fecha_original.month, fecha_original.day)
            
            # Actualizar la evaluación
            eval.fecha = nueva_fecha
            eval.save()
            
            actualizadas += 1
            
            # Mostrar progreso cada 100 evaluaciones
            if actualizadas % 100 == 0:
                print(f"✅ Actualizadas: {actualizadas}/{total}")
                
        except Exception as e:
            print(f"❌ Error actualizando evaluación {eval.id}: {e}")
            errores += 1
    
    print(f"\n🎉 Actualización completada!")
    print(f"✅ Evaluaciones actualizadas: {actualizadas}")
    print(f"❌ Errores: {errores}")
    
    # Verificar el resultado
    primera_eval_nueva = Evaluacion.objects.first()
    ultima_eval_nueva = Evaluacion.objects.last()
    print(f"📅 Nuevo rango: {primera_eval_nueva.fecha} a {ultima_eval_nueva.fecha}")

if __name__ == "__main__":
    actualizar_fechas_evaluaciones() 