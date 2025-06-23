#!/usr/bin/env python
"""
Script para poblar las asignaturas electivas en la base de datos
Crea asignaturas electivas para 3° y 4° medio con sus docentes asignados
"""

import os
import sys
import django
import random

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Asignatura, AsignaturaImpartida, Docente, Especialidad

def poblar_electivos():
    """Pobla las asignaturas electivas para 3° y 4° medio"""
    print("🎯 Poblando asignaturas electivas...")
    
    # Verificar si ya existen electivos
    electivos_existentes = Asignatura.objects.filter(es_electivo=True).count()
    if electivos_existentes > 0:
        print(f"⚠️ Ya existen {electivos_existentes} asignaturas electivas en la base de datos.")
        print("¿Deseas continuar y crear nuevas asignaturas impartidas? (s/n): ", end="")
        respuesta = input().lower()
        if respuesta != 's':
            print("❌ Proceso cancelado.")
            return
    
    # Definir electivos por nivel
    electivos_por_nivel = {
        3: [
            'Matemáticas Aplicadas',
            'Literatura Avanzada', 
            'Historia del Arte',
            'Biología Molecular',
            'Física Cuántica',
            'Química Orgánica',
            'Taller de Debate y Oratoria',
            'Programación Avanzada'
        ],
        4: [
            'Cálculo Avanzado',
            'Literatura Contemporánea',
            'Historia Universal',
            'Biología Celular',
            'Física Moderna',
            'Química Analítica',
            'Taller de Redacción',
            'Desarrollo Web'
        ]
    }
    
    # Obtener docentes disponibles
    docentes = list(Docente.objects.all())
    if not docentes:
        print("❌ No hay docentes disponibles para asignar a electivos")
        return
    
    # Mapeo de especialidades para electivos
    mapeo_especialidades = {
        'Matemáticas Aplicadas': ['Matematicas', 'Fisica'],
        'Cálculo Avanzado': ['Matematicas', 'Fisica'],
        'Literatura Avanzada': ['Lenguaje', 'Historia'],
        'Literatura Contemporánea': ['Lenguaje', 'Historia'],
        'Historia del Arte': ['Historia', 'Arte'],
        'Historia Universal': ['Historia'],
        'Biología Molecular': ['Biologia', 'Quimica'],
        'Biología Celular': ['Biologia', 'Quimica'],
        'Física Cuántica': ['Fisica', 'Matematicas'],
        'Física Moderna': ['Fisica', 'Matematicas'],
        'Química Orgánica': ['Quimica', 'Biologia'],
        'Química Analítica': ['Quimica', 'Biologia'],
        'Taller de Debate y Oratoria': ['Lenguaje'],
        'Taller de Redacción': ['Lenguaje'],
        'Programación Avanzada': ['Tecnología'],
        'Desarrollo Web': ['Tecnología']
    }
    
    electivos_creados = 0
    asignaturas_impartidas_creadas = 0
    
    for nivel, electivos in electivos_por_nivel.items():
        print(f"\n📚 Creando electivos para {nivel}° medio:")
        
        for electivo_nombre in electivos:
            # Crear o obtener la asignatura electiva
            asignatura, created = Asignatura.objects.get_or_create(
                nombre=electivo_nombre,
                defaults={
                    'nivel': nivel,
                    'es_electivo': True
                }
            )
            
            if created:
                electivos_creados += 1
                print(f"  ✅ Creada asignatura: {electivo_nombre}")
            
            # Buscar docente apropiado según especialidad
            especialidades_buscadas = mapeo_especialidades.get(electivo_nombre, [])
            docente_asignado = None
            
            # Primero buscar docentes con especialidad exacta
            for especialidad_nombre in especialidades_buscadas:
                docentes_especialidad = [d for d in docentes if d.especialidad and d.especialidad.nombre == especialidad_nombre]
                if docentes_especialidad:
                    docente_asignado = random.choice(docentes_especialidad)
                    break
            
            # Si no hay docente con especialidad exacta, asignar uno aleatorio
            if not docente_asignado:
                docente_asignado = random.choice(docentes)
            
            # Crear código único para evitar duplicados
            codigo_base = f"{electivo_nombre[:3].upper()}{nivel}E"
            codigo = codigo_base
            contador = 1
            
            # Verificar si el código ya existe y generar uno único
            while AsignaturaImpartida.objects.filter(codigo=codigo).exists():
                codigo = f"{codigo_base}{contador}"
                contador += 1
            
            # Crear AsignaturaImpartida
            try:
                asignatura_imp, created = AsignaturaImpartida.objects.get_or_create(
                    asignatura=asignatura,
                    docente=docente_asignado,
                    defaults={'codigo': codigo}
                )
                
                if created:
                    asignaturas_impartidas_creadas += 1
                    print(f"    📝 Asignado docente: {docente_asignado.usuario.nombre} {docente_asignado.usuario.apellido_paterno} ({docente_asignado.especialidad.nombre if docente_asignado.especialidad else 'Sin especialidad'}) - Código: {codigo}")
                else:
                    print(f"    ⚠️ Ya existe: {electivo_nombre} con código {asignatura_imp.codigo}")
                    
            except Exception as e:
                print(f"    ❌ Error creando {electivo_nombre}: {e}")
    
    print(f"\n🎉 ¡Proceso completado!")
    print(f"📊 Resumen:")
    print(f"   • Asignaturas electivas creadas: {electivos_creados}")
    print(f"   • Asignaturas impartidas creadas: {asignaturas_impartidas_creadas}")
    print(f"   • Total de electivos disponibles: {Asignatura.objects.filter(es_electivo=True).count()}")

if __name__ == "__main__":
    poblar_electivos() 