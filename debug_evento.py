#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import CalendarioColegio, AuthUser

def debug_crear_evento():
    print("🔍 Depurando sistema de eventos...")
    
    # 1. Verificar usuarios admins
    print("\n1️⃣ Verificando usuarios administradores:")
    admins = AuthUser.objects.filter(is_admin=True)
    print(f"   Total admins: {admins.count()}")
    
    if admins.count() == 0:
        print("   ⚠️ No hay admins. Creando uno...")
        admin = AuthUser.objects.create_user(
            rut='12345678',
            div='9',
            password='admin123'
        )
        admin.is_admin = True
        admin.save()
        print(f"   ✅ Admin creado: {admin.rut}-{admin.div}")
    else:
        for admin in admins:
            print(f"   👤 Admin: {admin.rut}-{admin.div}")
    
    # 2. Verificar eventos existentes
    print("\n2️⃣ Verificando eventos existentes:")
    eventos_existentes = CalendarioColegio.objects.all()
    print(f"   Total eventos: {eventos_existentes.count()}")
    
    for evento in eventos_existentes[:3]:  # Mostrar solo los primeros 3
        print(f"   📅 {evento.nombre_actividad} - {evento.fecha}")
    
    # 3. Crear evento de prueba
    print("\n3️⃣ Creando evento de prueba:")
    try:
        evento_prueba = CalendarioColegio.objects.create(
            nombre_actividad="Evento Debug Modal",
            descripcion="Evento creado para depurar el modal mejorado",
            fecha="2025-01-20",
            hora="14:00:00",
            ubicacion="Sala de Sistemas",
            encargado="Admin Debug"
        )
        
        print(f"   ✅ Evento creado:")
        print(f"      ID: {evento_prueba.id}")
        print(f"      Título: {evento_prueba.nombre_actividad}")
        print(f"      Fecha: {evento_prueba.fecha}")
        print(f"      Hora: {evento_prueba.hora}")
        
        # 4. Verificar que se guardó correctamente
        print("\n4️⃣ Verificando persistencia:")
        evento_verificacion = CalendarioColegio.objects.get(id=evento_prueba.id)
        print(f"   ✅ Evento recuperado: {evento_verificacion.nombre_actividad}")
        
        print(f"\n📊 Resumen final:")
        print(f"   Total eventos ahora: {CalendarioColegio.objects.count()}")
        print(f"   Último evento: {CalendarioColegio.objects.last().nombre_actividad}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_crear_evento() 