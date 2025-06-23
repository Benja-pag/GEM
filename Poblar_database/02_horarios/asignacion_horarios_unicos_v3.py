import os
import django
import sys
from datetime import date, time
from collections import defaultdict
import random

# Agrega el directorio raíz del proyecto al path (sube dos niveles desde subcarpeta)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Curso, Clase, Asignatura, AsignaturaImpartida, Docente, Especialidad

def es_asignatura_especial(asignatura):
    """Determina si una asignatura puede ocupar solo 1 bloque."""
    asignaturas_especiales = ['Música', 'Arte', 'Filosofía', 'Educación Física']
    return asignatura.nombre in asignaturas_especiales

def es_asignatura_bloque_impar(asignatura):
    """Determina si una asignatura debe ir en bloques impares."""
    asignaturas_bloque_impar = ['Educación Física', 'Arte', 'Música']
    return asignatura.nombre in asignaturas_bloque_impar

def obtener_asignaturas_por_nivel(nivel):
    """Obtiene las asignaturas correspondientes a cada nivel."""
    if nivel in [1, 2]:
        # 1° y 2° Medio: Solo asignaturas obligatorias
        return Asignatura.objects.filter(
            nombre__in=['Matemáticas', 'Lenguaje', 'Historia', 'Biología', 'Física', 'Química', 'Educación Física', 'Arte', 'Música']
        ).exclude(nombre__in=['Filosofía'])  # Filosofía solo en 3°-4°
    else:
        # 3° y 4° Medio: Incluye Filosofía
        return Asignatura.objects.filter(
            nombre__in=['Matemáticas', 'Lenguaje', 'Historia', 'Biología', 'Física', 'Química', 'Educación Física', 'Arte', 'Música', 'Filosofía']
        )

def obtener_docente_por_especialidad(asignatura, docentes_por_asignatura, docentes_ocupados):
    """Obtiene un docente según la especialidad de la asignatura o relacionada."""
    if asignatura.nombre in docentes_por_asignatura:
        return docentes_por_asignatura[asignatura.nombre]
    
    # Mapeo de asignaturas a especialidades (incluyendo relacionadas)
    mapeo_especialidades = {
        'Matemáticas': ['Matemáticas', 'Física'],  # Físicos pueden dar matemáticas
        'Lenguaje': ['Lenguaje', 'Historia'],      # Historiadores pueden dar lenguaje
        'Historia': ['Historia', 'Lenguaje'],      # Profesores de lenguaje pueden dar historia
        'Biología': ['Biología', 'Química'],       # Químicos pueden dar biología
        'Física': ['Física', 'Matemáticas'],       # Matemáticos pueden dar física
        'Química': ['Química', 'Biología'],        # Biólogos pueden dar química
        'Educación Física': ['Educación Física'],
        'Arte': ['Arte'],
        'Música': ['Música'],
        'Filosofía': ['Filosofía', 'Historia']     # Historiadores pueden dar filosofía
    }
    
    especialidades_buscadas = mapeo_especialidades.get(asignatura.nombre, [])
    
    # Buscar docentes con la especialidad correspondiente o relacionada
    docentes_disponibles = []
    for docente in Docente.objects.all():
        if docente.especialidad and docente.especialidad.nombre in especialidades_buscadas:
            # Verificar que el docente no esté ocupado en el mismo bloque
            if docente not in docentes_ocupados:
                docentes_disponibles.append(docente)
    
    if docentes_disponibles:
        docente_elegido = random.choice(docentes_disponibles)
        docentes_por_asignatura[asignatura.nombre] = docente_elegido
        docentes_ocupados.add(docente_elegido)
        return docente_elegido
    else:
        # Si no hay docentes con especialidad relacionada, buscar cualquier docente disponible
        docentes_todos = [d for d in Docente.objects.all() if d not in docentes_ocupados]
        if docentes_todos:
            docente_elegido = random.choice(docentes_todos)
            docentes_por_asignatura[asignatura.nombre] = docente_elegido
            docentes_ocupados.add(docente_elegido)
            return docente_elegido
        else:
            # Si todos están ocupados, elegir uno al azar
            docente_elegido = random.choice(list(Docente.objects.all()))
            docentes_por_asignatura[asignatura.nombre] = docente_elegido
            return docente_elegido

def generar_horario_curso(curso):
    """Genera el horario específico para un curso según las reglas."""
    print(f"\n📚 Generando horario para {curso} (Nivel {curso.nivel})")
    
    # Obtener asignaturas del nivel
    asignaturas = list(obtener_asignaturas_por_nivel(curso.nivel))
    
    # Definir estructura de bloques según nivel
    if curso.nivel in [1, 2]:
        # 1° y 2° Medio: bloques 1-9 (lun-jue), 1-6 (viernes)
        estructura_bloques = {
            'LUNES': ['1-2', '3-4', '5-6', '7-8', '9'],
            'MARTES': ['1-2', '3-4', '5-6', '7-8', '9'],
            'MIERCOLES': ['1-2', '3-4', '5-6', '7-8', '9'],
            'JUEVES': ['1-2', '3-4', '5-6', '7-8', '9'],
            'VIERNES': ['1-2', '3-4', '5-6']
        }
    else:
        # 3° y 4° Medio: obligatorias 1-6, electivos 7-9 (solo lun-jue)
        estructura_bloques = {
            'LUNES': ['1-2', '3-4', '5-6', '7-8', '9'],
            'MARTES': ['1-2', '3-4', '5-6', '7-8', '9'],
            'MIERCOLES': ['1-2', '3-4', '5-6', '7-8', '9'],
            'JUEVES': ['1-2', '3-4', '5-6', '7-8', '9'],
            'VIERNES': ['1-2', '3-4', '5-6']
        }
    
    # Limpiar clases existentes del curso
    Clase.objects.filter(curso=curso).delete()
    AsignaturaImpartida.objects.filter(clases__curso=curso).delete()
    
    # Diccionario para rastrear asignaciones
    horario_curso = {}
    asignaturas_asignadas = defaultdict(int)
    
    # Diccionario para evitar duplicados de AsignaturaImpartida y docente fijo
    asignaturas_impartidas = {}
    docentes_por_asignatura = {}
    docentes_ocupados = set()  # Para evitar conflictos de horarios
    
    # Frecuencias objetivo
    frecuencias = {
        'Matemáticas': 4, 'Lenguaje': 4, 'Historia': 3, 'Biología': 3,
        'Física': 3, 'Química': 3, 'Educación Física': 2, 'Arte': 2, 'Música': 2
    }
    if curso.nivel in [3, 4]:
        frecuencias['Filosofía'] = 2
    
    # Asignar asignaturas regulares (pares de bloques)
    asignaturas_regulares = [a for a in asignaturas if not es_asignatura_especial(a)]
    
    for asignatura in asignaturas_regulares:
        # Obtener docente según especialidad
        docente = obtener_docente_por_especialidad(asignatura, docentes_por_asignatura, docentes_ocupados)
        pares_asignados = 0
        max_intentos = 50
        codigo = f"{asignatura.nombre[:3].upper()}{curso.nivel}{curso.letra}"
        if asignatura.nombre not in asignaturas_impartidas:
            asignatura_imp, _ = AsignaturaImpartida.objects.get_or_create(
                asignatura=asignatura, docente=docente, codigo=codigo
            )
            asignaturas_impartidas[asignatura.nombre] = asignatura_imp
        else:
            asignatura_imp = asignaturas_impartidas[asignatura.nombre]
        
        while pares_asignados < frecuencias.get(asignatura.nombre, 3) and max_intentos > 0:
            # Buscar un par de bloques disponible
            asignacion_exitosa = False
            
            for dia in ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']:
                if asignacion_exitosa:
                    break
                    
                for bloque_grupo in estructura_bloques[dia]:
                    if bloque_grupo in ['1-2', '3-4', '5-6', '7-8'] and dia not in horario_curso:
                        horario_curso[dia] = {}
                    
                    if bloque_grupo in ['1-2', '3-4', '5-6', '7-8']:
                        # Es un par de bloques
                        if dia not in horario_curso:
                            horario_curso[dia] = {}
                        
                        if bloque_grupo not in horario_curso[dia]:
                            # Asignar el par
                            bloques = bloque_grupo.split('-')
                            for bloque in bloques:
                                Clase.objects.create(
                                    asignatura_impartida=asignatura_imp,
                                    curso=curso,
                                    fecha=dia,
                                    horario=bloque,
                                    sala=f"SALA-{curso.nivel}{curso.letra}"
                                )
                            
                            horario_curso[dia][bloque_grupo] = asignatura.nombre
                            asignaturas_asignadas[asignatura.nombre] += 1
                            pares_asignados += 1
                            asignacion_exitosa = True
                            print(f"  ✅ {asignatura.nombre} en {dia} {bloque_grupo} - {docente.usuario.nombre} {docente.usuario.apellido_paterno} ({docente.especialidad.nombre})")
                            break
            
            max_intentos -= 1
    
    # Asignar asignaturas especiales solo en bloques individuales (9) para evitar aislamiento
    asignaturas_especiales = [a for a in asignaturas if es_asignatura_especial(a)]
    
    for asignatura in asignaturas_especiales:
        # Obtener docente según especialidad
        docente = obtener_docente_por_especialidad(asignatura, docentes_por_asignatura, docentes_ocupados)
        bloques_asignados = 0
        max_intentos = 30
        codigo = f"{asignatura.nombre[:3].upper()}{curso.nivel}{curso.letra}"
        if asignatura.nombre not in asignaturas_impartidas:
            asignatura_imp, _ = AsignaturaImpartida.objects.get_or_create(
                asignatura=asignatura, docente=docente, codigo=codigo
            )
            asignaturas_impartidas[asignatura.nombre] = asignatura_imp
        else:
            asignatura_imp = asignaturas_impartidas[asignatura.nombre]
        
        while bloques_asignados < frecuencias.get(asignatura.nombre, 2) and max_intentos > 0:
            asignacion_exitosa = False
            
            for dia in ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES']:
                if asignacion_exitosa:
                    break
                    
                # Solo asignar en bloque 9 para evitar aislamiento
                bloque_grupo = '9'
                if dia not in horario_curso:
                    horario_curso[dia] = {}
                
                if bloque_grupo not in horario_curso[dia]:
                    Clase.objects.create(
                        asignatura_impartida=asignatura_imp,
                        curso=curso,
                        fecha=dia,
                        horario=bloque_grupo,
                        sala=f"SALA-{curso.nivel}{curso.letra}"
                    )
                    
                    horario_curso[dia][bloque_grupo] = asignatura.nombre
                    asignaturas_asignadas[asignatura.nombre] += 1
                    bloques_asignados += 1
                    asignacion_exitosa = True
                    print(f"  ✅ {asignatura.nombre} en {dia} bloque {bloque_grupo} - {docente.usuario.nombre} {docente.usuario.apellido_paterno} ({docente.especialidad.nombre})")
                    break
            
            max_intentos -= 1
    
    print(f"  📊 Asignaturas asignadas: {dict(asignaturas_asignadas)}")

def poblar_horarios_v3():
    """Pobla los horarios cumpliendo todas las reglas específicas."""
    print("🧹 Borrando clases y asignaturas impartidas...")
    Clase.objects.all().delete()
    AsignaturaImpartida.objects.all().delete()
    
    print("🎯 Generando horarios según reglas específicas...")
    
    cursos = Curso.objects.all().order_by('nivel', 'letra')
    
    for curso in cursos:
        generar_horario_curso(curso)
    
    print("\n✅ Poblamiento de horarios V3 completado.")
    print("🔍 Ejecuta 'python Poblar_database\\06_verificacion\\verificar_horario.py' para verificar los resultados.")

if __name__ == "__main__":
    poblar_horarios_v3() 