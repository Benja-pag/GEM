#!/usr/bin/env python
"""
Script simple para diagnosticar problemas con PDF
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Estudiante, Usuario, Administrativo

def check_basic_data():
    """Verificar datos básicos"""
    
    print("🔍 Verificando datos básicos...")
    
    # Estudiantes
    estudiantes = Estudiante.objects.all()
    print(f"📊 Estudiantes en BD: {estudiantes.count()}")
    
    if estudiantes.count() > 0:
        estudiante = estudiantes.first()
        print(f"   - Primer estudiante: {estudiante.usuario.get_full_name()} (ID: {estudiante.pk})")
    
    # Usuarios admin
    admins = Administrativo.objects.filter(rol='ADMINISTRADOR')
    print(f"👑 Administradores: {admins.count()}")
    
    if admins.count() > 0:
        admin = admins.first()
        print(f"   - Primer admin: {admin.usuario.get_full_name()}")
    
    return estudiantes.count() > 0 and admins.count() > 0

def check_urls():
    """Verificar URLs"""
    
    print("\n🔗 Verificando URLs...")
    
    from django.conf import settings
    from Core import urls
    
    # Buscar la URL en el archivo urls.py
    print("📋 URLs configuradas en Core/urls.py:")
    
    # Leer el archivo urls.py
    import inspect
    url_patterns = []
    
    try:
        # Verificar que la vista existe
        from Core.views.pdf_views import DescargarAsistenciaEstudiantePDFView
        print("✅ Vista DescargarAsistenciaEstudiantePDFView encontrada")
        
        # Verificar URL directa
        url = "/pdf/reporte-asistencia-estudiante/"
        print(f"🔗 URL esperada: {url}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando vista: {e}")
        return False

def generate_test_url():
    """Generar URL de prueba"""
    
    print("\n🧪 Generando URL de prueba...")
    
    estudiantes = Estudiante.objects.all()[:1]
    if not estudiantes:
        print("❌ No hay estudiantes")
        return None
    
    estudiante = estudiantes[0]
    url = f"/pdf/reporte-asistencia-estudiante/?estudiante_id={estudiante.pk}&periodo=ano_actual"
    
    print(f"🔗 URL de prueba: {url}")
    print(f"📝 Para estudiante: {estudiante.usuario.get_full_name()}")
    
    return url

def generate_javascript():
    """Generar código JavaScript de prueba"""
    
    print("\n💻 Código JavaScript para probar en consola del navegador:")
    print("=" * 60)
    
    estudiantes = Estudiante.objects.all()[:1]
    if not estudiantes:
        print("❌ No hay estudiantes")
        return
    
    estudiante = estudiantes[0]
    nombre = estudiante.usuario.get_full_name()
    
    js_code = f"""
// Probar en la consola del navegador:

// 1. Verificar que la función existe:
console.log(typeof window.descargarPDFEstudianteDirecto);

// 2. Si devuelve 'function', ejecutar:
window.descargarPDFEstudianteDirecto({estudiante.pk}, '{nombre}');

// 3. Si devuelve 'undefined', verificar:
console.log(typeof descargarPDFEstudianteDirecto);

// 4. O probar directamente la URL:
window.open('/pdf/reporte-asistencia-estudiante/?estudiante_id={estudiante.pk}&periodo=ano_actual', '_blank');
"""
    
    print(js_code)

if __name__ == "__main__":
    print("🚀 Diagnóstico Simple de PDF")
    print("=" * 50)
    
    # Verificar datos básicos
    data_ok = check_basic_data()
    
    if not data_ok:
        print("❌ Faltan datos básicos en la BD")
        sys.exit(1)
    
    # Verificar URLs
    urls_ok = check_urls()
    
    if not urls_ok:
        print("❌ Problema con URLs")
        sys.exit(1)
    
    # Generar URL de prueba
    test_url = generate_test_url()
    
    # Generar JavaScript
    generate_javascript()
    
    print("\n" + "=" * 50)
    print("✅ Diagnóstico completado")
    print("\n🔧 Pasos para depurar:")
    print("1. Abre el navegador en: http://localhost:8000/admin-panel/")
    print("2. Ve a: Reportes > Asistencia > Por Estudiante") 
    print("3. Abre herramientas de desarrollador (F12)")
    print("4. Ve a la pestaña 'Console'")
    print("5. Ejecuta el código JavaScript mostrado arriba")
    print("6. Si hay errores, cópialos aquí para ayudarte") 