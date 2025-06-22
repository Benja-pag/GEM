import os
import django
import sys

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models.cursos import Curso, Clase, AsignaturaImpartida

def corregir_horario_1A():
    """
    Corrige los datos del horario del curso 1°A
    """
    print("="*70)
    print("CORRECCIÓN DE HORARIO - CURSO 1°A")
    print("="*70)
    
    try:
        # Obtener el curso 1°A
        curso = Curso.objects.get(nivel=1, letra='A')
        print(f"\nCurso encontrado: {curso}")
        
        # Obtener todas las clases del curso 1°A
        clases = Clase.objects.filter(curso=curso)
        print(f"Total de clases antes de la corrección: {clases.count()}")
        
        # Mostrar clases con horarios incorrectos
        clases_incorrectas = clases.filter(horario__in=['10', '11', '12'])
        if clases_incorrectas.exists():
            print(f"\n❌ Clases con horarios incorrectos encontradas: {clases_incorrectas.count()}")
            for clase in clases_incorrectas:
                print(f"  - {clase.asignatura_impartida.asignatura.nombre} - {clase.fecha} - Horario: {clase.horario}")
            
            # Eliminar clases con horarios incorrectos
            clases_incorrectas.delete()
            print("✅ Clases con horarios incorrectos eliminadas")
        
        # Verificar horarios válidos
        bloques_validos = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        clases_validas = clases.filter(horario__in=bloques_validos)
        print(f"Clases con horarios válidos: {clases_validas.count()}")
        
        # Mostrar distribución actual por día
        print(f"\n📊 DISTRIBUCIÓN ACTUAL POR DÍA:")
        dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
        
        for dia in dias:
            clases_dia = clases_validas.filter(fecha=dia).order_by('horario')
            print(f"\n{dia}:")
            if clases_dia.exists():
                for clase in clases_dia:
                    print(f"  - Bloque {clase.horario}: {clase.asignatura_impartida.asignatura.nombre} - {clase.asignatura_impartida.docente.usuario.nombre}")
            else:
                print("  - Sin clases")
        
        # Mostrar estadísticas finales
        print(f"\n📈 ESTADÍSTICAS FINALES:")
        print(f"• Total de clases válidas: {clases_validas.count()}")
        print(f"• Asignaturas diferentes: {clases_validas.values('asignatura_impartida__asignatura__nombre').distinct().count()}")
        print(f"• Docentes diferentes: {clases_validas.values('asignatura_impartida__docente__usuario__nombre').distinct().count()}")
        
        # Verificar si hay conflictos (mismo día, mismo bloque, diferentes asignaturas)
        print(f"\n🔍 VERIFICANDO CONFLICTOS:")
        conflictos = []
        for dia in dias:
            for bloque in bloques_validos:
                clases_bloque = clases_validas.filter(fecha=dia, horario=bloque)
                if clases_bloque.count() > 1:
                    conflictos.append({
                        'dia': dia,
                        'bloque': bloque,
                        'clases': list(clases_bloque)
                    })
        
        if conflictos:
            print(f"❌ Se encontraron {len(conflictos)} conflictos:")
            for conflicto in conflictos:
                print(f"  - {conflicto['dia']} Bloque {conflicto['bloque']}:")
                for clase in conflicto['clases']:
                    print(f"    * {clase.asignatura_impartida.asignatura.nombre}")
        else:
            print("✅ No se encontraron conflictos de horario")
        
    except Curso.DoesNotExist:
        print("❌ Error: No se encontró el curso 1°A en la base de datos")
    except Exception as e:
        print(f"❌ Error al corregir el horario: {str(e)}")

def mostrar_horario_corregido():
    """
    Muestra el horario corregido del curso 1°A
    """
    try:
        curso = Curso.objects.get(nivel=1, letra='A')
        print(f"\n{'HORARIO CORREGIDO DEL CURSO 1°A':^70}")
        print("="*70)
        
        # Obtener clases válidas
        bloques_validos = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        clases = Clase.objects.filter(
            curso=curso,
            horario__in=bloques_validos
        ).select_related(
            'asignatura_impartida__asignatura',
            'asignatura_impartida__docente__usuario'
        ).order_by('fecha', 'horario')
        
        dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
        
        for dia in dias:
            print(f"\n{'='*20} {dia} {'='*20}")
            clases_dia = clases.filter(fecha=dia).order_by('horario')
            
            if clases_dia.exists():
                for clase in clases_dia:
                    # Mostrar horario en formato legible
                    if clase.horario == '1':
                        horario_texto = "08:00-08:45"
                    elif clase.horario == '2':
                        horario_texto = "08:45-09:30"
                    elif clase.horario == '3':
                        horario_texto = "09:45-10:30"
                    elif clase.horario == '4':
                        horario_texto = "10:30-11:15"
                    elif clase.horario == '5':
                        horario_texto = "11:30-12:15"
                    elif clase.horario == '6':
                        horario_texto = "12:15-13:00"
                    elif clase.horario == '7':
                        horario_texto = "13:45-14:30"
                    elif clase.horario == '8':
                        horario_texto = "14:30-15:15"
                    elif clase.horario == '9':
                        horario_texto = "15:15-16:00"
                    else:
                        horario_texto = f"Bloque {clase.horario}"
                    
                    print(f"• {horario_texto} - {clase.asignatura_impartida.asignatura.nombre}")
                    print(f"  Docente: {clase.asignatura_impartida.docente.usuario.nombre} {clase.asignatura_impartida.docente.usuario.apellido_paterno}")
                    print(f"  Sala: {clase.sala}")
                    print()
            else:
                print("  No hay clases programadas")
        
    except Curso.DoesNotExist:
        print("❌ Error: No se encontró el curso 1°A en la base de datos")
    except Exception as e:
        print(f"❌ Error al mostrar el horario corregido: {str(e)}")

if __name__ == "__main__":
    # Corregir el horario
    corregir_horario_1A()
    
    # Mostrar el horario corregido
    mostrar_horario_corregido()
    
    print("\n" + "="*70)
    print("FIN DE LA CORRECCIÓN")
    print("="*70) 