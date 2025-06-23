import os
import django
import sys
from collections import defaultdict
from datetime import date, time

# Agrega el directorio raíz del proyecto al path (sube dos niveles desde subcarpeta)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Curso, Clase

def verificar_consistencia_docentes():
    """
    Verifica que cada asignatura en un curso específico sea impartida por un único docente.
    """
    print("🔍 Iniciando verificación de consistencia de docentes por asignatura y curso...")
    
    # Usaremos un diccionario para rastrear qué docentes enseñan qué asignatura en cada curso
    # Estructura: {(id_curso, id_asignatura): set(id_docente)}
    asignaciones = defaultdict(set)

    # Obtenemos todas las clases, precargando los datos relacionados para eficiencia
    clases = Clase.objects.select_related(
        'curso',
        'asignatura_impartida__asignatura',
        'asignatura_impartida__docente__usuario'
    ).all()

    # Llenamos nuestro diccionario con los datos de la base de datos
    for clase in clases:
        curso = clase.curso
        asignatura = clase.asignatura_impartida.asignatura
        docente = clase.asignatura_impartida.docente
        
        clave = (f"{curso.nivel}°{curso.letra}", asignatura.nombre)
        nombre_docente = f"{docente.usuario.nombre} {docente.usuario.apellido_paterno}"
        
        asignaciones[clave].add(nombre_docente)

    # Ahora, revisamos los datos en busca de inconsistencias
    print("\n--- INFORME DE CONSISTENCIA DE DOCENTES ---")
    errores_encontrados = 0
    
    # Ordenamos por curso y luego por asignatura para un reporte más legible
    for (curso_nombre, asignatura_nombre), docentes in sorted(asignaciones.items()):
        if len(docentes) > 1:
            if errores_encontrados == 0:
                print("Se encontraron las siguientes inconsistencias:")
            
            print(f"\n  ❌ ERROR en: {curso_nombre} - Asignatura: {asignatura_nombre}")
            print(f"     Docentes asignados: {', '.join(sorted(list(docentes)))}")
            errores_encontrados += 1
    
    if errores_encontrados == 0:
        print("\n✅ ¡Verificación completada! Todas las asignaturas son impartidas por un único docente por curso. No hay inconsistencias.")
    else:
        print(f"\n🚨 ¡Verificación completada! Se encontraron {errores_encontrados} inconsistencias.")

if __name__ == "__main__":
    verificar_consistencia_docentes() 