import os
import django
import sys
from datetime import date

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import (
    Estudiante, Curso, AsignaturaImpartida, AsignaturaInscrita, Clase
)

def limpiar_inscripciones_anteriores():
    """
    Limpia todas las inscripciones anteriores de estudiantes
    """
    print("🧹 Limpiando inscripciones anteriores...")
    inscripciones_eliminadas = AsignaturaInscrita.objects.all().delete()
    print(f"✅ Se eliminaron {inscripciones_eliminadas[0]} inscripciones anteriores")

def obtener_estudiantes_por_curso():
    """
    Obtiene todos los estudiantes agrupados por curso
    """
    estudiantes_por_curso = {}
    
    for curso in Curso.objects.all().order_by('nivel', 'letra'):
        estudiantes = Estudiante.objects.filter(curso=curso).order_by('usuario__apellido_paterno', 'usuario__nombre')
        if estudiantes.exists():
            estudiantes_por_curso[curso] = list(estudiantes)
    
    return estudiantes_por_curso

def obtener_asignaturas_impartidas_por_curso():
    """
    Obtiene las asignaturas impartidas agrupadas por curso
    """
    asignaturas_por_curso = {}
    
    for curso in Curso.objects.all().order_by('nivel', 'letra'):
        # Obtener asignaturas impartidas que tienen clases en este curso
        asignaturas_impartidas = AsignaturaImpartida.objects.filter(
            clases__curso=curso
        ).distinct().order_by('asignatura__nombre')
        
        if asignaturas_impartidas.exists():
            asignaturas_por_curso[curso] = list(asignaturas_impartidas)
    
    return asignaturas_por_curso

def inscribir_estudiantes_automaticamente():
    """
    Inscribe automáticamente a todos los estudiantes en las asignaturas impartidas de sus cursos
    """
    print("🎓 INSCRIPCIÓN AUTOMÁTICA DE ESTUDIANTES")
    print("="*60)
    
    # Limpiar inscripciones anteriores
    limpiar_inscripciones_anteriores()
    
    # Obtener datos
    estudiantes_por_curso = obtener_estudiantes_por_curso()
    asignaturas_por_curso = obtener_asignaturas_impartidas_por_curso()
    
    total_inscripciones = 0
    total_estudiantes = 0
    
    print(f"\n📚 Procesando {len(estudiantes_por_curso)} cursos...")
    
    for curso, estudiantes in estudiantes_por_curso.items():
        print(f"\n🎯 Curso: {curso}")
        print(f"   Estudiantes: {len(estudiantes)}")
        
        # Obtener asignaturas impartidas para este curso
        asignaturas_impartidas = asignaturas_por_curso.get(curso, [])
        
        if not asignaturas_impartidas:
            print(f"   ⚠️ No hay asignaturas impartidas para {curso}")
            continue
        
        print(f"   Asignaturas impartidas: {len(asignaturas_impartidas)}")
        
        # Inscribir cada estudiante en todas las asignaturas impartidas del curso
        for estudiante in estudiantes:
            estudiante_nombre = f"{estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}"
            inscripciones_estudiante = 0
            
            for asignatura_impartida in asignaturas_impartidas:
                # Crear inscripción
                inscripcion, created = AsignaturaInscrita.objects.get_or_create(
                    estudiante=estudiante,
                    asignatura_impartida=asignatura_impartida,
                    defaults={
                        'fecha_inscripcion': date.today(),
                        'validada': True  # Automáticamente validada
                    }
                )
                
                if created:
                    inscripciones_estudiante += 1
                    total_inscripciones += 1
            
            print(f"     ✅ {estudiante_nombre}: {inscripciones_estudiante} asignaturas inscritas")
            total_estudiantes += 1
    
    return total_inscripciones, total_estudiantes

def mostrar_resumen_inscripciones():
    """
    Muestra un resumen de las inscripciones realizadas
    """
    print(f"\n📊 RESUMEN DE INSCRIPCIONES")
    print("="*60)
    
    # Estadísticas por curso
    for curso in Curso.objects.all().order_by('nivel', 'letra'):
        estudiantes_curso = Estudiante.objects.filter(curso=curso).count()
        asignaturas_curso = AsignaturaImpartida.objects.filter(clases__curso=curso).distinct().count()
        inscripciones_curso = AsignaturaInscrita.objects.filter(
            estudiante__curso=curso
        ).count()
        
        print(f"\n🎓 {curso}:")
        print(f"   - Estudiantes: {estudiantes_curso}")
        print(f"   - Asignaturas impartidas: {asignaturas_curso}")
        print(f"   - Total inscripciones: {inscripciones_curso}")
        
        if estudiantes_curso > 0 and asignaturas_curso > 0:
            inscripciones_esperadas = estudiantes_curso * asignaturas_curso
            if inscripciones_curso == inscripciones_esperadas:
                print(f"   ✅ Inscripciones completas")
            else:
                print(f"   ⚠️ Faltan {inscripciones_esperadas - inscripciones_curso} inscripciones")
    
    # Estadísticas generales
    total_estudiantes = Estudiante.objects.count()
    total_asignaturas_impartidas = AsignaturaImpartida.objects.distinct().count()
    total_inscripciones = AsignaturaInscrita.objects.count()
    
    print(f"\n📈 ESTADÍSTICAS GENERALES:")
    print(f"   - Total estudiantes: {total_estudiantes}")
    print(f"   - Total asignaturas impartidas: {total_asignaturas_impartidas}")
    print(f"   - Total inscripciones: {total_inscripciones}")
    
    if total_estudiantes > 0 and total_asignaturas_impartidas > 0:
        inscripciones_esperadas = total_estudiantes * total_asignaturas_impartidas
        if total_inscripciones == inscripciones_esperadas:
            print(f"   ✅ Todas las inscripciones fueron realizadas correctamente")
        else:
            print(f"   ⚠️ Faltan {inscripciones_esperadas - total_inscripciones} inscripciones")

def verificar_inscripciones():
    """
    Verifica que las inscripciones se hayan realizado correctamente
    """
    print(f"\n🔍 VERIFICANDO INSCRIPCIONES")
    print("="*60)
    
    errores_encontrados = 0
    
    for curso in Curso.objects.all().order_by('nivel', 'letra'):
        estudiantes = Estudiante.objects.filter(curso=curso)
        asignaturas_impartidas = AsignaturaImpartida.objects.filter(clases__curso=curso).distinct()
        
        if not estudiantes.exists():
            continue
            
        if not asignaturas_impartidas.exists():
            continue
        
        print(f"\n🎓 Verificando {curso}:")
        
        for estudiante in estudiantes:
            estudiante_nombre = f"{estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno}"
            inscripciones_estudiante = AsignaturaInscrita.objects.filter(
                estudiante=estudiante,
                asignatura_impartida__in=asignaturas_impartidas
            )
            
            if inscripciones_estudiante.count() == asignaturas_impartidas.count():
                print(f"   ✅ {estudiante_nombre}: {inscripciones_estudiante.count()} asignaturas inscritas")
            else:
                print(f"   ❌ {estudiante_nombre}: Faltan inscripciones")
                errores_encontrados += 1
    
    if errores_encontrados == 0:
        print(f"\n✅ VERIFICACIÓN EXITOSA: Todas las inscripciones están correctas")
    else:
        print(f"\n❌ SE ENCONTRARON {errores_encontrados} ERRORES EN LAS INSCRIPCIONES")
    
    return errores_encontrados == 0

def main():
    """
    Función principal que ejecuta todo el proceso de inscripción
    """
    print("🎓 SISTEMA DE INSCRIPCIÓN AUTOMÁTICA DE ESTUDIANTES")
    print("="*60)
    
    try:
        # Realizar inscripciones
        total_inscripciones, total_estudiantes = inscribir_estudiantes_automaticamente()
        
        print(f"\n✅ INSCRIPCIÓN COMPLETADA:")
        print(f"   - Estudiantes procesados: {total_estudiantes}")
        print(f"   - Inscripciones realizadas: {total_inscripciones}")
        
        # Mostrar resumen
        mostrar_resumen_inscripciones()
        
        # Verificar inscripciones
        verificacion_exitosa = verificar_inscripciones()
        
        if verificacion_exitosa:
            print(f"\n🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
            print(f"Todos los estudiantes han sido inscritos en sus asignaturas correspondientes.")
        else:
            print(f"\n⚠️ EL PROCESO SE COMPLETÓ PERO SE ENCONTRARON PROBLEMAS")
            print(f"Revisa los errores mostrados arriba.")
            
    except Exception as e:
        print(f"\n❌ ERROR DURANTE EL PROCESO: {str(e)}")
        print(f"Detalles del error: {type(e).__name__}")

if __name__ == "__main__":
    main() 