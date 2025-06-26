#!/usr/bin/env python
import os
import django
import requests
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import CalendarioColegio, AuthUser

def test_crear_evento():
    print("🧪 Probando creación de evento del administrador...")
    
    # Verificar que existe al menos un admin
    admin = AuthUser.objects.filter(is_admin=True).first()
    if not admin:
        print("❌ No hay usuarios administradores en la base de datos")
        return
    
    print(f"✅ Admin encontrado: {admin.rut}-{admin.div}")
    
    # Datos de prueba para crear evento
    datos_evento = {
        'titulo': 'Evento de Prueba - Modal Mejorado',
        'tipo': 'Colegio',
        'fecha': '2025-01-15',
        'hora': '10:30',
        'descripcion': 'Evento creado desde el modal mejorado para probar funcionalidad',
        'ubicacion': 'Auditorio',
        'encargado': 'Dirección'
    }
    
    print(f"\n📋 Datos del evento:")
    for key, value in datos_evento.items():
        print(f"   {key}: {value}")
    
    # Crear evento directamente en la base de datos
    try:
        evento = CalendarioColegio.objects.create(
            nombre_actividad=datos_evento['titulo'],
            descripcion=datos_evento['descripcion'],
            fecha=datos_evento['fecha'],
            hora=datos_evento['hora'],
            ubicacion=datos_evento['ubicacion'],
            encargado=datos_evento['encargado']
        )
        
        print(f"\n✅ Evento creado exitosamente:")
        print(f"   ID: {evento.id}")
        print(f"   Título: {evento.nombre_actividad}")
        print(f"   Fecha: {evento.fecha}")
        print(f"   Hora: {evento.hora}")
        print(f"   Ubicación: {evento.ubicacion}")
        print(f"   Encargado: {evento.encargado}")
        
        # Verificar que se puede recuperar
        evento_recuperado = CalendarioColegio.objects.get(id=evento.id)
        print(f"\n🔍 Verificación - Evento recuperado: {evento_recuperado.nombre_actividad}")
        
        # Contar total de eventos
        total_eventos = CalendarioColegio.objects.count()
        print(f"📊 Total de eventos en CalendarioColegio: {total_eventos}")
        
    except Exception as e:
        print(f"❌ Error al crear evento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_crear_evento() 