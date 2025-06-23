import os
import django
import sys
from collections import defaultdict

# Agrega el directorio raíz del proyecto al path (sube dos niveles desde subcarpeta)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Curso, Clase, Asignatura, AsignaturaImpartida

def obtener_asignaturas_obligatorias_por_nivel():
    """Define las asignaturas obligatorias por nivel según el archivo de datos base."""
    asignaturas_obligatorias = {
        1: ['Matemáticas', 'Lenguaje', 'Historia', 'Biología', 'Física', 'Química', 'Inglés', 'Educación Física', 'Arte', 'Música', 'Tecnología'],
        2: ['Matemáticas', 'Lenguaje', 'Historia', 'Biología', 'Física', 'Química', 'Inglés', 'Educación Física', 'Arte', 'Música', 'Tecnología'],
        3: ['Matemáticas', 'Lenguaje', 'Historia', 'Biología', 'Física', 'Química', 'Inglés', 'Educación Física', 'Filosofía'],
        4: ['Matemáticas', 'Lenguaje', 'Historia', 'Biología', 'Física', 'Química', 'Inglés', 'Educación Física', 'Filosofía']
    }
    return asignaturas_obligatorias

def verificar_asignaturas_obligatorias():
    """
    Verifica que todas las asignaturas obligatorias se estén impartiendo en todos los cursos.
    """
    print("🔍 Verificando asignaturas obligatorias en todos los cursos...")
    
    asignaturas_obligatorias = obtener_asignaturas_obligatorias_por_nivel()
    cursos = Curso.objects.all().order_by('nivel', 'letra')
    
    errores_encontrados = 0
    resumen_por_curso = {}
    
    for curso in cursos:
        print(f"\n📚 Verificando curso: {curso} (Nivel {curso.nivel})")
        
        # Obtener asignaturas obligatorias para este nivel
        asignaturas_requeridas = asignaturas_obligatorias.get(curso.nivel, [])
        
        # Obtener asignaturas que se están impartiendo en este curso
        clases_curso = Clase.objects.filter(curso=curso)
        asignaturas_impartidas = set()
        
        for clase in clases_curso:
            asignatura_nombre = clase.asignatura_impartida.asignatura.nombre
            asignaturas_impartidas.add(asignatura_nombre)
        
        # Verificar asignaturas faltantes
        asignaturas_faltantes = []
        for asignatura in asignaturas_requeridas:
            if asignatura not in asignaturas_impartidas:
                asignaturas_faltantes.append(asignatura)
                errores_encontrados += 1
        
        # Verificar asignaturas extra (no obligatorias)
        asignaturas_extra = []
        for asignatura in asignaturas_impartidas:
            if asignatura not in asignaturas_requeridas:
                asignaturas_extra.append(asignatura)
        
        # Mostrar resultados
        if asignaturas_faltantes:
            print(f"  ❌ ASIGNATURAS FALTANTES: {', '.join(asignaturas_faltantes)}")
        else:
            print(f"  ✅ Todas las asignaturas obligatorias están siendo impartidas")
        
        if asignaturas_extra:
            print(f"  ⚠️ ASIGNATURAS EXTRA (no obligatorias): {', '.join(asignaturas_extra)}")
        
        # Mostrar resumen de asignaturas impartidas
        print(f"  📊 Asignaturas impartidas ({len(asignaturas_impartidas)}): {', '.join(sorted(asignaturas_impartidas))}")
        
        # Guardar resumen
        resumen_por_curso[curso] = {
            'requeridas': asignaturas_requeridas,
            'impartidas': list(asignaturas_impartidas),
            'faltantes': asignaturas_faltantes,
            'extra': asignaturas_extra
        }
    
    # Mostrar resumen general
    print(f"\n{'='*60}")
    print("📋 RESUMEN GENERAL")
    print(f"{'='*60}")
    
    for curso, datos in resumen_por_curso.items():
        estado = "✅ COMPLETO" if not datos['faltantes'] else "❌ INCOMPLETO"
        print(f"{curso}: {estado}")
        if datos['faltantes']:
            print(f"  Faltantes: {', '.join(datos['faltantes'])}")
    
    print(f"\n{'='*60}")
    if errores_encontrados == 0:
        print("🎉 ¡VERIFICACIÓN EXITOSA! Todos los cursos tienen todas sus asignaturas obligatorias.")
    else:
        print(f"🚨 Se encontraron {errores_encontrados} asignaturas obligatorias faltantes en total.")
    
    return errores_encontrados == 0

def verificar_frecuencia_asignaturas():
    """
    Verifica la frecuencia de cada asignatura por curso.
    """
    print(f"\n{'='*60}")
    print("📊 VERIFICACIÓN DE FRECUENCIA DE ASIGNATURAS")
    print(f"{'='*60}")
    
    cursos = Curso.objects.all().order_by('nivel', 'letra')
    
    for curso in cursos:
        print(f"\n📚 {curso}:")
        
        # Contar frecuencia de cada asignatura
        clases_curso = Clase.objects.filter(curso=curso)
        frecuencia_asignaturas = defaultdict(int)
        
        for clase in clases_curso:
            asignatura_nombre = clase.asignatura_impartida.asignatura.nombre
            frecuencia_asignaturas[asignatura_nombre] += 1
        
        # Mostrar frecuencia
        for asignatura, frecuencia in sorted(frecuencia_asignaturas.items()):
            print(f"  {asignatura}: {frecuencia} veces")

if __name__ == "__main__":
    print("🔍 INICIANDO VERIFICACIÓN DE ASIGNATURAS OBLIGATORIAS")
    print("=" * 60)
    
    # Verificar asignaturas obligatorias
    verificacion_exitosa = verificar_asignaturas_obligatorias()
    
    # Verificar frecuencia
    verificar_frecuencia_asignaturas()
    
    print(f"\n{'='*60}")
    if verificacion_exitosa:
        print("✅ VERIFICACIÓN COMPLETADA - TODAS LAS ASIGNATURAS OBLIGATORIAS ESTÁN PRESENTES")
    else:
        print("❌ VERIFICACIÓN COMPLETADA - HAY ASIGNATURAS OBLIGATORIAS FALTANTES")
    print(f"{'='*60}") 