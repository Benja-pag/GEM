import os
import django
import sys

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Asignatura, Curso, Estudiante, Usuario

print("=== PRUEBA DE ASIGNATURAS ELECTIVAS ===\n")

# Simular la lógica de la vista para diferentes niveles
for nivel in [3, 4]:
    print(f"📚 PRUEBA PARA {nivel}° MEDIO:")
    
    # Simular la consulta de la vista
    electivos = Asignatura.objects.filter(
        es_electivo=True,
        nivel=nivel
    ).prefetch_related('imparticiones__docente__usuario')
    
    if electivos.exists():
        print(f"  ✅ Se encontraron {electivos.count()} electivos:")
        for electivo in electivos:
            print(f"    • {electivo.nombre}")
            
            # Verificar si tiene profesores asignados
            impartidas = electivo.imparticiones.all()
            if impartidas.exists():
                print(f"      Profesores: {', '.join([f'{i.docente.usuario.nombre} {i.docente.usuario.apellido_paterno}' for i in impartidas])}")
            else:
                print(f"      Profesores: No asignado")
    else:
        print(f"  ❌ No se encontraron electivos para {nivel}° medio")

print("\n🔍 VERIFICACIÓN DE CURSOS:")
# Verificar que existen cursos de 3° y 4° medio
cursos_3_4 = Curso.objects.filter(nivel__in=[3, 4])
if cursos_3_4.exists():
    print("  ✅ Cursos de 3° y 4° medio encontrados:")
    for curso in cursos_3_4:
        print(f"    • {curso}")
else:
    print("  ❌ No se encontraron cursos de 3° y 4° medio")

print("\n👥 VERIFICACIÓN DE ESTUDIANTES:")
# Verificar que hay estudiantes en cursos de 3° y 4° medio
estudiantes_3_4 = Estudiante.objects.filter(curso__nivel__in=[3, 4])
if estudiantes_3_4.exists():
    print(f"  ✅ Se encontraron {estudiantes_3_4.count()} estudiantes en 3° y 4° medio:")
    for estudiante in estudiantes_3_4[:5]:  # Mostrar solo los primeros 5
        print(f"    • {estudiante.usuario.nombre} {estudiante.usuario.apellido_paterno} - {estudiante.curso}")
    if estudiantes_3_4.count() > 5:
        print(f"    ... y {estudiantes_3_4.count() - 5} más")
else:
    print("  ❌ No se encontraron estudiantes en 3° y 4° medio")

print("\n✅ PRUEBA COMPLETADA") 