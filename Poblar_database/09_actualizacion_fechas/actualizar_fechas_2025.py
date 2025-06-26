#!/usr/bin/env python
"""
Script para actualizar las fechas de evaluaciones al año actual (2025)
Parte del sistema de poblado de la base de datos
"""
import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Evaluacion

def actualizar_fechas_evaluaciones_2025():
    """
    Actualiza todas las fechas de evaluaciones al año actual (2025)
    Mantiene el mes y día originales, solo cambia el año
    """
    
    print("🔄 [PASO 9] Actualizando fechas de evaluaciones a 2025...")
    
    # Obtener todas las evaluaciones
    evaluaciones = Evaluacion.objects.all()
    total = evaluaciones.count()
    
    print(f"📊 Total de evaluaciones encontradas: {total}")
    
    if total == 0:
        print("❌ No hay evaluaciones para actualizar")
        return True
    
    # Mostrar rango actual de fechas
    primera_eval = evaluaciones.first()
    ultima_eval = evaluaciones.last()
    print(f"📅 Rango actual: {primera_eval.fecha} a {ultima_eval.fecha}")
    
    # Verificar si ya están en 2025
    if primera_eval.fecha.year == 2025:
        print("✅ Las evaluaciones ya están en 2025, no es necesario actualizar")
        return True
    
    # Actualizar fechas
    actualizadas = 0
    errores = 0
    año_actual = 2025
    
    print(f"🔄 Actualizando {total} evaluaciones al año {año_actual}...")
    
    for eval in evaluaciones:
        try:
            fecha_original = eval.fecha
            
            # Cambiar solo el año a 2025, mantener mes y día
            nueva_fecha = date(año_actual, fecha_original.month, fecha_original.day)
            
            # Actualizar la evaluación
            eval.fecha = nueva_fecha
            eval.save()
            
            actualizadas += 1
            
            # Mostrar progreso cada 200 evaluaciones
            if actualizadas % 200 == 0:
                print(f"   ✅ Progreso: {actualizadas}/{total} evaluaciones actualizadas")
                
        except Exception as e:
            print(f"   ❌ Error actualizando evaluación {eval.id}: {e}")
            errores += 1
    
    print(f"\n🎉 Actualización de fechas completada!")
    print(f"   ✅ Evaluaciones actualizadas: {actualizadas}")
    print(f"   ❌ Errores: {errores}")
    
    # Verificar el resultado
    if actualizadas > 0:
        primera_eval_nueva = Evaluacion.objects.first()
        ultima_eval_nueva = Evaluacion.objects.last()
        print(f"   📅 Nuevo rango: {primera_eval_nueva.fecha} a {ultima_eval_nueva.fecha}")
    
    return errores == 0

def main():
    """Función principal para ejecutar el script independientemente"""
    try:
        exito = actualizar_fechas_evaluaciones_2025()
        if exito:
            print("✅ Script completado exitosamente")
            sys.exit(0)
        else:
            print("❌ Script completado con errores")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 