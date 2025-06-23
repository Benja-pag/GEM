import os
import django
import sys
import random
from collections import defaultdict
from datetime import date, time

# Agrega el directorio raíz del proyecto al path (sube dos niveles desde subcarpeta)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import (
    Clase, AsignaturaImpartida, Curso, Docente, Asignatura, Especialidad
)

def obtener_asignaturas_obligatorias_por_nivel():
    """Obtiene las asignaturas obligatorias por nivel"""
    asignaturas_por_nivel = {
        1: [],  # 1° medio
        2: [],  # 2° medio
        3: [],  # 3° medio
        4: [],  # 4° medio
    }
    
    for nivel in [1, 2]:
        asignaturas = Asignatura.objects.filter(
            nivel=nivel,
            es_electivo=False,
            nombre__in=[
                'Lenguaje', 'Matemáticas', 'Historia', 'Biología', 
                'Física', 'Química', 'Inglés', 'Educación Física', 
                'Arte', 'Música', 'Tecnología'
            ]
        )
        asignaturas_por_nivel[nivel] = list(asignaturas)
    
    # Asignaturas obligatorias para 3° y 4° medio
    for nivel in [3, 4]:
        asignaturas = Asignatura.objects.filter(
            nivel=nivel,
            es_electivo=False,
            nombre__in=[
                'Lenguaje', 'Matemáticas', 'Historia', 'Biología', 
                'Física', 'Química', 'Inglés', 'Educación Física', 'Filosofía'
            ]
        )
        asignaturas_por_nivel[nivel] = list(asignaturas)
    
    return asignaturas_por_nivel

def obtener_docentes_por_especialidad():
    """Obtiene un diccionario con los docentes agrupados por especialidad"""
    docentes_especialidad = {}
    
    for docente in Docente.objects.all():
        especialidad = docente.especialidad.nombre
        if especialidad not in docentes_especialidad:
            docentes_especialidad[especialidad] = []
        docentes_especialidad[especialidad].append(docente)
    
    return docentes_especialidad

def verificar_especialidad_docente(nombre_asignatura, especialidad_docente):
    """Verifica si un docente puede impartir una asignatura según su especialidad"""
    equivalencias = {
        "Matematicas": ["Matemáticas", "Matemática Avanzada", "Matemáticas Discretas", "Estadística y Análisis de Datos"],
        "Matemáticas Discretas": ["Matemáticas", "Matemática Avanzada", "Matemáticas Discretas", "Estadística y Análisis de Datos"],
        "Estadística y Análisis de Datos": ["Matemáticas", "Matemática Avanzada", "Matemáticas Discretas", "Estadística y Análisis de Datos"],
        
        "Lenguaje": ["Lenguaje", "Literatura y Escritura Creativa"],
        "Literatura y Escritura Creativa": ["Lenguaje", "Literatura y Escritura Creativa"],
        
        "Historia": ["Historia", "Historia del Arte y Cultura", "Sociología y Estudios Sociales"],
        "Historia del Arte y Cultura": ["Historia", "Historia del Arte y Cultura", "Sociología y Estudios Sociales"],
        "Sociología y Estudios Sociales": ["Historia", "Historia del Arte y Cultura", "Sociología y Estudios Sociales"],
        
        "Biologia": ["Biología", "Biología Avanzada"],
        "Biología Avanzada": ["Biología", "Biología Avanzada"],
        
        "Fisica": ["Física", "Física Aplicada"],
        "Física Aplicada": ["Física", "Física Aplicada"],
        
        "Quimica": ["Química", "Química Experimental"],
        "Química Experimental": ["Química", "Química Experimental"],
        
        "Ingles": ["Inglés"],
        "Educación Fisica": ["Educación Física"],
        "Arte": ["Arte", "Teatro y Expresión Corporal", "Música y Composición"],
        "Tecnologia": ["Tecnología", "Programación y Robótica", "Tecnología e Innovación"],
        "Filosofía y Ética": ["Filosofía"],
        "Psicología y Desarrollo Humano": ["Psicología y Desarrollo Humano"],
        "Música y Composición": ["Música"],
        "Teatro y Expresión Corporal": ["Arte"],
        "Programación y Robótica": ["Tecnología", "Programación y Robótica", "Tecnología e Innovación"],
        "Tecnología e Innovación": ["Tecnología", "Programación y Robótica", "Tecnología e Innovación"],
    }
    
    if especialidad_docente in equivalencias:
        return nombre_asignatura in equivalencias[especialidad_docente]
    return False

def obtener_docente_para_asignatura(asignatura, docentes_especialidad):
    """Obtiene un docente disponible para una asignatura"""
    docentes_potenciales = []
    for especialidad, docentes in docentes_especialidad.items():
        if verificar_especialidad_docente(asignatura.nombre, especialidad):
            docentes_potenciales.extend(docentes)
    
    if docentes_potenciales:
        return random.choice(docentes_potenciales)
    return None

def crear_horarios_segun_reglas():
    """
    Crea horarios siguiendo EXACTAMENTE las reglas especificadas:
    - Bloques pares (2 bloques seguidos) para asignaturas principales
    - Bloques impares (1 bloque) para asignaturas especiales
    - Diferentes configuraciones para cursos A y B
    """
    print("🧹 Limpiando datos antiguos...")
    AsignaturaImpartida.objects.all().delete()
    Clase.objects.all().delete()
    
    print("📚 Obteniendo datos necesarios...")
    cursos = list(Curso.objects.all().order_by('nivel', 'letra'))
    asignaturas_por_nivel = obtener_asignaturas_obligatorias_por_nivel()
    docentes_especialidad = obtener_docentes_por_especialidad()
    
    # Contadores para seguimiento
    total_asignaturas_impartidas = 0
    total_clases_creadas = 0
    contador_codigo = 1
    
    print("\n🎯 CREANDO HORARIOS SEGÚN REGLAS ESPECÍFICAS")
    print("="*60)
    
    for curso in cursos:
        print(f"\n📚 Procesando {curso}...")
        
        # Obtener asignaturas para este nivel
        asignaturas_nivel = asignaturas_por_nivel.get(curso.nivel, [])
        if not asignaturas_nivel:
            print(f"  ⚠️ No hay asignaturas para nivel {curso.nivel}")
            continue
        
        # Separar asignaturas por tipo
        asignaturas_principales = [a for a in asignaturas_nivel if a.nombre not in ['Arte', 'Música', 'Filosofía', 'Educación Física']]
        asignaturas_especiales = [a for a in asignaturas_nivel if a.nombre in ['Arte', 'Música', 'Filosofía', 'Educación Física']]
        
        # Crear estructura de horario según el tipo de curso
        horario_curso = crear_estructura_horario_curso(curso, asignaturas_principales, asignaturas_especiales)
        
        # Asignar docentes y crear clases
        asignaturas_impartidas_curso = 0
        clases_creadas_curso = 0
        
        for dia, bloques_dia in horario_curso.items():
            for bloque, asignatura in bloques_dia.items():
                if asignatura == "ELECTIVO":
                    continue
                
                # Obtener docente
                docente = obtener_docente_para_asignatura(asignatura, docentes_especialidad)
                if not docente:
                    print(f"    ⚠️ No hay docente para {asignatura.nombre}")
                    continue
                
                # Crear código único para AsignaturaImpartida
                codigo = f"{asignatura.nombre[:3].upper()}_{curso.nivel}{curso.letra}_{docente.usuario.apellido_paterno[:3].upper()}_{contador_codigo:03d}"
                contador_codigo += 1
                
                # Crear AsignaturaImpartida si no existe
                asignatura_impartida, created = AsignaturaImpartida.objects.get_or_create(
                    asignatura=asignatura,
                    docente=docente,
                    codigo=codigo
                )
                if created:
                    asignaturas_impartidas_curso += 1
                    total_asignaturas_impartidas += 1
                
                # Crear clase
                clase = Clase.objects.create(
                    curso=curso,
                    asignatura_impartida=asignatura_impartida,
                    fecha=dia,
                    horario=bloque,
                    sala=obtener_sala_para_asignatura(asignatura)
                )
                clases_creadas_curso += 1
                total_clases_creadas += 1
                
                print(f"    ✓ {dia} {bloque}: {asignatura.nombre} - {docente.usuario.nombre}")
        
        print(f"  📊 {curso}: {asignaturas_impartidas_curso} asignaturas, {clases_creadas_curso} clases")
    
    print(f"\n✅ PROCESO COMPLETADO:")
    print(f"   - Total asignaturas impartidas: {total_asignaturas_impartidas}")
    print(f"   - Total clases creadas: {total_clases_creadas}")

def crear_estructura_horario_curso(curso, asignaturas_principales, asignaturas_especiales):
    """
    Crea la estructura de horario según las reglas específicas para cada tipo de curso
    """
    horario = {}
    
    if curso.nivel in [1, 2]:  # 1° y 2° medio
        if curso.letra == 'A':
            horario = crear_horario_curso_a(asignaturas_principales, asignaturas_especiales)
        else:  # curso.letra == 'B'
            horario = crear_horario_curso_b(asignaturas_principales, asignaturas_especiales)
    else:  # 3° y 4° medio
        horario = crear_horario_curso_superior(asignaturas_principales, asignaturas_especiales)
    
    return horario

def crear_horario_curso_a(asignaturas_principales, asignaturas_especiales):
    """
    Horario para 1°A y 2°A:
    - Bloques 1-2: principal (doble)
    - Bloques 3-4: principal (doble)
    - Bloques 5-6: principal (doble)
    - Bloque 7: especial (impar)
    - Bloques 8-9: principal (doble)
    """
    horario = {}
    dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
    
    # Mezclar asignaturas para distribución aleatoria
    principales = asignaturas_principales.copy()
    especiales = asignaturas_especiales.copy()
    random.shuffle(principales)
    random.shuffle(especiales)
    
    idx_principal = 0
    idx_especial = 0
    
    for dia in dias:
        horario[dia] = {}
        # Asignar bloques dobles (1-2, 3-4, 5-6, 8-9)
        for bloque_doble in [(1,2), (3,4), (5,6), (8,9)]:
            if idx_principal >= len(principales):
                idx_principal = 0  # Reiniciar si se acaban
            asignatura = principales[idx_principal]
            horario[dia][str(bloque_doble[0])] = asignatura
            horario[dia][str(bloque_doble[1])] = asignatura
            idx_principal += 1
        # Bloque 7: especial
        if idx_especial >= len(especiales):
            idx_especial = 0  # Reiniciar si se acaban
        if especiales:
            horario[dia]['7'] = especiales[idx_especial]
            idx_especial += 1
        else:
            # Si no hay especiales, usar principal
            horario[dia]['7'] = principales[idx_principal % len(principales)]
    
        # Viernes solo bloques 1-6
        if dia == 'VIERNES':
            for b in ['7','8','9']:
                if b in horario[dia]:
                    del horario[dia][b]
    return horario

def crear_horario_curso_b(asignaturas_principales, asignaturas_especiales):
    """
    Horario para 1°B y 2°B:
    - Bloques 1-2: principal (doble)
    - Bloques 3-4: principal (doble)
    - Bloques 5-6: principal (doble)
    - Bloques 7-8: principal (doble)
    - Bloque 9: especial (impar)
    """
    horario = {}
    dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
    
    # Mezclar asignaturas para distribución aleatoria
    principales = asignaturas_principales.copy()
    especiales = asignaturas_especiales.copy()
    random.shuffle(principales)
    random.shuffle(especiales)
    
    idx_principal = 0
    idx_especial = 0
    
    for dia in dias:
        horario[dia] = {}
        # Asignar bloques dobles (1-2, 3-4, 5-6, 7-8)
        for bloque_doble in [(1,2), (3,4), (5,6), (7,8)]:
            if idx_principal >= len(principales):
                idx_principal = 0  # Reiniciar si se acaban
            asignatura = principales[idx_principal]
            horario[dia][str(bloque_doble[0])] = asignatura
            horario[dia][str(bloque_doble[1])] = asignatura
            idx_principal += 1
        # Bloque 9: especial
        if idx_especial >= len(especiales):
            idx_especial = 0  # Reiniciar si se acaban
        if especiales:
            horario[dia]['9'] = especiales[idx_especial]
            idx_especial += 1
        else:
            # Si no hay especiales, usar principal
            horario[dia]['9'] = principales[idx_principal % len(principales)]
    
        # Viernes solo bloques 1-6
        if dia == 'VIERNES':
            for b in ['7','8','9']:
                if b in horario[dia]:
                    del horario[dia][b]
    return horario

def crear_horario_curso_superior(asignaturas_principales, asignaturas_especiales):
    """
    Horario para 3°A, 3°B, 4°A, 4°B:
    - Solo bloques 1-6 (como si todos los días fueran viernes)
    - Bloques 1-2: principal (doble)
    - Bloques 3-4: principal (doble)
    - Bloques 5-6: principal (doble)
    - Bloques 7, 8, 9 marcados como "ELECTIVO"
    """
    horario = {}
    dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
    
    # Mezclar asignaturas para distribución aleatoria
    principales = asignaturas_principales.copy()
    especiales = asignaturas_especiales.copy()
    random.shuffle(principales)
    random.shuffle(especiales)
    
    idx_principal = 0
    idx_especial = 0
    
    for dia in dias:
        horario[dia] = {}
        # Solo bloques 1-6, agrupados en dobles
        for bloque_doble in [(1,2), (3,4), (5,6)]:
            if idx_principal >= len(principales):
                idx_principal = 0  # Reiniciar si se acaban
            asignatura = principales[idx_principal]
            horario[dia][str(bloque_doble[0])] = asignatura
            horario[dia][str(bloque_doble[1])] = asignatura
            idx_principal += 1
        
        # Bloques 7, 8, 9 marcados como ELECTIVO
        for bloque in ['7', '8', '9']:
            horario[dia][bloque] = "ELECTIVO"
    
    return horario

def obtener_sala_para_asignatura(asignatura):
    """Asigna una sala según la asignatura"""
    salas_especiales = {
        'Educación Física': 'GIMNASIO',
        'Arte': 'SALA_8',
        'Música': 'SALA_8',
        'Tecnología': 'LAB_COMP',
        'Física': 'LAB_CIEN',
        'Química': 'LAB_CIEN',
        'Biología': 'LAB_CIEN',
    }
    
    return salas_especiales.get(asignatura.nombre, 'SALA_1')

if __name__ == "__main__":
    crear_horarios_segun_reglas() 