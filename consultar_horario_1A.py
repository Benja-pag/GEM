import os
import django
import sys
from datetime import datetime

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models.cursos import Curso, Clase, AsignaturaImpartida
from Core.models.usuarios import Docente

def mostrar_horario_curso_1A():
    """
    Muestra el horario completo del curso 1°A en formato de tabla
    """
    try:
        # Obtener el curso 1°A
        curso = Curso.objects.get(nivel=1, letra='A')
        print(f"\n{'='*80}")
        print(f"HORARIO DEL CURSO {curso}")
        print(f"{'='*80}")
        
        # Definir los días y bloques
        dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
        bloques = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        
        # Obtener todas las clases del curso 1°A
        clases = Clase.objects.filter(
            curso=curso
        ).select_related(
            'asignatura_impartida__asignatura',
            'asignatura_impartida__docente__usuario'
        ).order_by('fecha', 'horario')
        
        # Crear diccionario para organizar las clases por día y bloque
        horario = {}
        for dia in dias:
            horario[dia] = {}
            for bloque in bloques:
                horario[dia][bloque] = None
        
        # Llenar el horario con las clases
        for clase in clases:
            if clase.fecha in horario and clase.horario in horario[clase.fecha]:
                horario[clase.fecha][clase.horario] = {
                    'asignatura': clase.asignatura_impartida.asignatura.nombre,
                    'docente': f"{clase.asignatura_impartida.docente.usuario.nombre} {clase.asignatura_impartida.docente.usuario.apellido_paterno}",
                    'sala': clase.sala,
                    'codigo': clase.asignatura_impartida.codigo
                }
        
        # Mostrar encabezado de la tabla
        print(f"{'HORARIO':<15}", end="")
        for dia in dias:
            print(f"{dia:<15}", end="")
        print()
        print("-" * 90)
        
        # Mostrar cada bloque
        for bloque in bloques:
            # Mostrar el horario del bloque
            if bloque == '1':
                horario_texto = "08:00-08:45"
            elif bloque == '2':
                horario_texto = "08:45-09:30"
            elif bloque == '3':
                horario_texto = "09:45-10:30"
            elif bloque == '4':
                horario_texto = "10:30-11:15"
            elif bloque == '5':
                horario_texto = "11:30-12:15"
            elif bloque == '6':
                horario_texto = "12:15-13:00"
            elif bloque == '7':
                horario_texto = "13:45-14:30"
            elif bloque == '8':
                horario_texto = "14:30-15:15"
            elif bloque == '9':
                horario_texto = "15:15-16:00"
            else:
                horario_texto = f"Bloque {bloque}"
            
            print(f"{horario_texto:<15}", end="")
            
            # Mostrar las clases para cada día
            for dia in dias:
                if horario[dia][bloque]:
                    clase_info = horario[dia][bloque]
                    # Mostrar asignatura y docente en formato compacto
                    texto = f"{clase_info['asignatura'][:8]}"
                    if len(clase_info['asignatura']) > 8:
                        texto += "..."
                    print(f"{texto:<15}", end="")
                else:
                    print(f"{'':<15}", end="")
            print()
            
            # Mostrar recreos y almuerzo
            if bloque == '2':
                print(f"{'RECREO':<15}", end="")
                for _ in dias:
                    print(f"{'':<15}", end="")
                print()
            elif bloque == '4':
                print(f"{'RECREO':<15}", end="")
                for _ in dias:
                    print(f"{'':<15}", end="")
                print()
            elif bloque == '6':
                print(f"{'ALMUERZO':<15}", end="")
                for _ in dias:
                    print(f"{'':<15}", end="")
                print()
        
        print("-" * 90)
        
        # Mostrar información detallada de las clases
        print(f"\n{'DETALLE DE CLASES':^80}")
        print(f"{'='*80}")
        
        for clase in clases:
            print(f"• {clase.asignatura_impartida.asignatura.nombre}")
            print(f"  - Docente: {clase.asignatura_impartida.docente.usuario.nombre} {clase.asignatura_impartida.docente.usuario.apellido_paterno}")
            print(f"  - Día: {clase.fecha}")
            print(f"  - Horario: {clase.horario}")
            print(f"  - Sala: {clase.sala}")
            print(f"  - Código: {clase.asignatura_impartida.codigo}")
            print()
        
        # Mostrar estadísticas
        total_clases = clases.count()
        asignaturas_unicas = clases.values('asignatura_impartida__asignatura__nombre').distinct().count()
        docentes_unicos = clases.values('asignatura_impartida__docente__usuario__nombre').distinct().count()
        
        print(f"{'ESTADÍSTICAS':^80}")
        print(f"{'='*80}")
        print(f"• Total de clases: {total_clases}")
        print(f"• Asignaturas diferentes: {asignaturas_unicas}")
        print(f"• Docentes diferentes: {docentes_unicos}")
        
    except Curso.DoesNotExist:
        print("❌ Error: No se encontró el curso 1°A en la base de datos")
    except Exception as e:
        print(f"❌ Error al consultar el horario: {str(e)}")

def mostrar_horario_por_dia():
    """
    Muestra el horario del curso 1°A organizado por día
    """
    try:
        curso = Curso.objects.get(nivel=1, letra='A')
        print(f"\n{'HORARIO DEL CURSO 1°A POR DÍA':^80}")
        print(f"{'='*80}")
        
        dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
        
        for dia in dias:
            print(f"\n{'='*20} {dia} {'='*20}")
            
            clases_dia = Clase.objects.filter(
                curso=curso,
                fecha=dia
            ).select_related(
                'asignatura_impartida__asignatura',
                'asignatura_impartida__docente__usuario'
            ).order_by('horario')
            
            if clases_dia.exists():
                for clase in clases_dia:
                    print(f"• {clase.horario} - {clase.asignatura_impartida.asignatura.nombre}")
                    print(f"  Docente: {clase.asignatura_impartida.docente.usuario.nombre} {clase.asignatura_impartida.docente.usuario.apellido_paterno}")
                    print(f"  Sala: {clase.sala}")
                    print()
            else:
                print("  No hay clases programadas")
        
    except Curso.DoesNotExist:
        print("❌ Error: No se encontró el curso 1°A en la base de datos")
    except Exception as e:
        print(f"❌ Error al consultar el horario por día: {str(e)}")

if __name__ == "__main__":
    print("CONSULTA DE HORARIO - CURSO 1°A")
    print("=" * 50)
    
    # Ejecutar automáticamente la opción 1 (mostrar horario completo)
    print("\nEjecutando consulta automática del horario completo...")
    mostrar_horario_curso_1A()
    
    print("\n" + "="*50)
    print("FIN DE LA CONSULTA")
    print("="*50) 