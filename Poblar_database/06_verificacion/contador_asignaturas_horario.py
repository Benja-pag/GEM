#!/usr/bin/env python
"""
Script simple: cuenta cuántas veces se repite cada asignatura en el horario general (HorarioCurso)
"""
import os
import sys
import django
from collections import Counter

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

try:
    from Core.models import AsignaturaImpartida, HorarioCurso
except Exception as e:
    print('❌ Error al importar modelos:', e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

def main():
    print('==============================')
    print('RECUENTO DE ASIGNATURAS EN HORARIO')
    print('==============================')
    
    # Contador de asignaturas
    contador = Counter()
    
    # Recorre todos los registros de HorarioCurso
    for h in HorarioCurso.objects.all().select_related('actividad'):
        # Si la actividad es una clase, buscamos la asignatura
        if h.actividad == 'CLASE':
            # Buscar la clase asociada a ese bloque y día
            # No hay relación directa, así que buscamos por bloque y día en AsignaturaImpartida
            # Este paso depende de cómo se relacione realmente HorarioCurso con AsignaturaImpartida
            # Si no hay relación, este script debe ser adaptado según la estructura real
            pass # Aquí deberías poner la lógica real si existe
    
    # Si tienes una relación directa, por ejemplo:
    # for h in HorarioCurso.objects.all().select_related('clase__asignatura_impartida__asignatura'):
    #     nombre = h.clase.asignatura_impartida.asignatura.nombre
    #     contador[nombre] += 1
    # Pero según tu modelo, no existe esa relación directa
    
    # Por ahora, solo muestro un mensaje de advertencia
    print('⚠️  No se puede contar asignaturas porque HorarioCurso no tiene relación directa con AsignaturaImpartida o Clase.')
    print('Adapta este script según la estructura real de tu modelo de horarios.')

if __name__ == "__main__":
    main() 