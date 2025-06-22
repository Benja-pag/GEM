import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Estudiante, Clase, Curso

print("🔍 CONSULTA SIMPLE DE HORARIOS")
print("="*50)

# 1. Consultar un alumno de 1°A
print("\n📚 ALUMNO 1°A:")
alumno_1a = Estudiante.objects.filter(curso__nivel=1, curso__letra='A').first()
if alumno_1a:
    print(f"Nombre: {alumno_1a.usuario.nombre} {alumno_1a.usuario.apellido_paterno}")
    print(f"Curso: {alumno_1a.curso}")
    
    # Obtener clases del curso
    clases_1a = Clase.objects.filter(curso=alumno_1a.curso).order_by('fecha', 'horario')
    print(f"Total clases: {clases_1a.count()}")
    
    # Mostrar horario por día
    dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
    for dia in dias:
        clases_dia = clases_1a.filter(fecha=dia).order_by('horario')
        if clases_dia.exists():
            print(f"\n{dia}:")
            for clase in clases_dia:
                asignatura = clase.asignatura_impartida.asignatura.nombre
                docente = f"{clase.asignatura_impartida.docente.usuario.nombre} {clase.asignatura_impartida.docente.usuario.apellido_paterno}"
                print(f"  Bloque {clase.horario}: {asignatura} - {docente} - {clase.sala}")
else:
    print("❌ No se encontró alumno en 1°A")

# 2. Consultar un alumno de 1°B
print("\n" + "="*50)
print("📚 ALUMNO 1°B:")
alumno_1b = Estudiante.objects.filter(curso__nivel=1, curso__letra='B').first()
if alumno_1b:
    print(f"Nombre: {alumno_1b.usuario.nombre} {alumno_1b.usuario.apellido_paterno}")
    print(f"Curso: {alumno_1b.curso}")
    
    # Obtener clases del curso
    clases_1b = Clase.objects.filter(curso=alumno_1b.curso).order_by('fecha', 'horario')
    print(f"Total clases: {clases_1b.count()}")
    
    # Mostrar horario por día
    for dia in dias:
        clases_dia = clases_1b.filter(fecha=dia).order_by('horario')
        if clases_dia.exists():
            print(f"\n{dia}:")
            for clase in clases_dia:
                asignatura = clase.asignatura_impartida.asignatura.nombre
                docente = f"{clase.asignatura_impartida.docente.usuario.nombre} {clase.asignatura_impartida.docente.usuario.apellido_paterno}"
                print(f"  Bloque {clase.horario}: {asignatura} - {docente} - {clase.sala}")
else:
    print("❌ No se encontró alumno en 1°B")

# 3. Resumen de asignaturas por curso
print("\n" + "="*50)
print("📊 RESUMEN DE ASIGNATURAS POR CURSO:")

for nivel in [1, 2]:
    for letra in ['A', 'B']:
        curso = Curso.objects.filter(nivel=nivel, letra=letra).first()
        if curso:
            clases_curso = Clase.objects.filter(curso=curso)
            asignaturas_unicas = clases_curso.values_list(
                'asignatura_impartida__asignatura__nombre', flat=True
            ).distinct()
            
            print(f"\n{curso}: {len(asignaturas_unicas)} asignaturas")
            for asignatura in sorted(asignaturas_unicas):
                print(f"  - {asignatura}")

print("\n✅ Consulta completada") 