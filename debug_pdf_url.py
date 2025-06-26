#!/usr/bin/env python
"""
Script para diagnosticar problemas con la descarga de PDF de asistencia
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Estudiante
from django.test import Client
from django.contrib.auth.models import User
from Core.models import Usuario

def test_pdf_url():
    """Probar la URL del PDF directamente"""
    
    print("🔍 Verificando configuración...")
    
    # Obtener un estudiante
    estudiantes = Estudiante.objects.all()[:1]
    if not estudiantes:
        print("❌ No hay estudiantes en la base de datos")
        return False
    
    estudiante = estudiantes[0]
    print(f"✅ Usando estudiante: {estudiante.usuario.get_full_name()} (ID: {estudiante.pk})")
    
    # Crear un cliente de prueba
    client = Client()
    
    # Intentar crear un usuario admin para la prueba
    try:
        # Buscar un usuario admin existente
        admin_user = Usuario.objects.filter(is_admin=True).first()
        if not admin_user:
            print("❌ No hay usuarios admin en la base de datos")
            return False
        
        print(f"✅ Usando admin: {admin_user.get_full_name()}")
        
        # Hacer login
        login_success = client.force_login(admin_user.user)
        print(f"✅ Login exitoso")
        
        # Construir URL
        url = f"/pdf/reporte-asistencia-estudiante/?estudiante_id={estudiante.pk}&periodo=ano_actual"
        print(f"🔗 URL a probar: {url}")
        
        # Hacer la petición
        print("📡 Haciendo petición...")
        response = client.get(url)
        
        print(f"📊 Código de respuesta: {response.status_code}")
        print(f"📄 Content-Type: {response.get('Content-Type', 'No especificado')}")
        print(f"📦 Tamaño de respuesta: {len(response.content)} bytes")
        
        if response.status_code == 200:
            content_type = response.get('Content-Type', '')
            if 'application/pdf' in content_type:
                print("✅ PDF generado correctamente")
                
                # Guardar el PDF para verificar
                filename = f"debug_pdf_{estudiante.pk}.pdf"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"💾 PDF guardado como: {filename}")
                
                return True
            else:
                print(f"❌ Respuesta no es PDF. Content-Type: {content_type}")
                print("📝 Contenido de respuesta:")
                print(response.content.decode('utf-8')[:500])
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print("📝 Contenido de respuesta:")
            print(response.content.decode('utf-8')[:500])
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_javascript_function():
    """Generar el código JavaScript que debería ejecutarse"""
    
    estudiantes = Estudiante.objects.all()[:3]
    if not estudiantes:
        print("❌ No hay estudiantes para generar JavaScript")
        return
    
    print("\n🔧 Código JavaScript que debería funcionar:")
    print("=" * 60)
    
    for estudiante in estudiantes:
        nombre_completo = estudiante.usuario.get_full_name()
        js_code = f"""
// Para estudiante: {nombre_completo}
descargarPDFEstudianteDirecto({estudiante.pk}, '{nombre_completo}');

// O alternativamente:
window.descargarPDFEstudianteDirecto({estudiante.pk}, '{nombre_completo}');

// URL que se debería generar:
// /pdf/reporte-asistencia-estudiante/?estudiante_id={estudiante.pk}&periodo=ano_actual
"""
        print(js_code)
        break  # Solo mostrar uno para no saturar

def check_urls():
    """Verificar que las URLs estén configuradas correctamente"""
    
    print("\n🔗 Verificando configuración de URLs...")
    
    from django.urls import reverse
    from django.core.exceptions import NoReverseMatch
    
    try:
        # Intentar resolver la URL
        url_name = 'descargar_asistencia_estudiante_pdf'
        try:
            url = reverse(url_name)
            print(f"✅ URL '{url_name}' configurada: {url}")
        except NoReverseMatch:
            print(f"❌ URL '{url_name}' no encontrada")
            
        # Verificar la URL directa
        direct_url = "/pdf/reporte-asistencia-estudiante/"
        print(f"🔗 URL directa: {direct_url}")
        
        # Verificar que la vista existe
        from Core.views.pdf_views import DescargarAsistenciaEstudiantePDFView
        print(f"✅ Vista DescargarAsistenciaEstudiantePDFView importada correctamente")
        
    except Exception as e:
        print(f"❌ Error verificando URLs: {str(e)}")

if __name__ == "__main__":
    print("🚀 Diagnóstico de PDF de asistencia de estudiante")
    print("=" * 60)
    
    # Verificar URLs
    check_urls()
    
    # Generar JavaScript de ejemplo
    test_javascript_function()
    
    # Probar URL directamente
    print("\n🧪 Probando URL directamente...")
    success = test_pdf_url()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ El PDF funciona correctamente en el backend")
        print("💡 El problema puede estar en el JavaScript del frontend")
        print("\n🔧 Pasos para depurar en el navegador:")
        print("1. Abre las herramientas de desarrollador (F12)")
        print("2. Ve a la pestaña 'Console'")
        print("3. Haz clic en el botón PDF")
        print("4. Verifica si hay errores JavaScript")
        print("5. Ve a la pestaña 'Network' para ver las peticiones HTTP")
    else:
        print("❌ Hay un problema en el backend")
        print("💡 Revisa los errores mostrados arriba")
    
    print("\n🌐 Para probar manualmente:")
    print("1. Ve a: http://localhost:8000/admin-panel/")
    print("2. Inicia sesión como administrador") 
    print("3. Ve a: Reportes > Asistencia > Por Estudiante")
    print("4. Haz clic en 'PDF Asistencia'") 