import os
import django
import sys
from datetime import date
from itertools import product
import random

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import (
    Clase, AsignaturaImpartida, Curso, Docente, Asignatura, Especialidad,
    HorarioCurso
)

def obtener_asignaturas_obligatorias_por_nivel():
    """Obtiene las asignaturas obligatorias por nivel para todos los cursos"""
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
        # Especialidades principales
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

def obtener_bloques_disponibles_por_curso(curso):
    """Obtiene los bloques disponibles para clases según el nivel del curso"""
    bloques_clase = []
    
    if curso.nivel in [1, 2]:  # 1° y 2° medio - horario completo
        # Bloques de lunes a jueves (todos los bloques)
        for dia in ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES']:
            for bloque in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                bloques_clase.append((dia, bloque))
        
        # Bloques del viernes (solo 1-6)
        for bloque in ['1', '2', '3', '4', '5', '6']:
            bloques_clase.append(('VIERNES', bloque))
    
    else:  # 3° y 4° medio - solo bloques 1-6
        # Bloques de lunes a viernes (solo 1-6)
        for dia in ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']:
            for bloque in ['1', '2', '3', '4', '5', '6']:
                bloques_clase.append((dia, bloque))
    
    return bloques_clase

def verificar_disponibilidad_docente(docente, dia, bloque, asignaciones_existentes):
    """Verifica si un docente está disponible en un bloque específico"""
    for asignacion in asignaciones_existentes:
        if (asignacion['docente'] == docente and 
            asignacion['dia'] == dia and 
            asignacion['bloque'] == bloque):
            return False
    return True

def asignar_sala_especial(asignatura):
    """Asigna una sala especial según la asignatura"""
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

def verificar_disponibilidad_bloques_consecutivos(dia, bloque_inicio, docente, curso, asignaciones_existentes):
    """Verifica si dos bloques consecutivos están disponibles para un docente y curso"""
    # Verificar que el bloque siguiente existe
    bloque_siguiente = str(int(bloque_inicio) + 1)
    
    # Si es viernes, solo hasta bloque 6
    if dia == "VIERNES" and int(bloque_inicio) >= 6:
        return False
    
    # Verificar conflictos para ambos bloques
    for bloque in [bloque_inicio, bloque_siguiente]:
        # Verificar si el docente ya tiene clase en ese horario
        for asignacion in asignaciones_existentes:
            if (asignacion['docente'] == docente and 
                asignacion['dia'] == dia and 
                asignacion['bloque'] == bloque):
                return False
        
        # Verificar si el curso ya tiene clase en ese horario
        for asignacion in asignaciones_existentes:
            if (asignacion['curso'] == curso and 
                asignacion['dia'] == dia and 
                asignacion['bloque'] == bloque):
                return False
    
    return True

def crear_asignaturas_impartidas_completas():
    """Crea asignaturas impartidas con horario completo para todos los cursos"""
    
    # Limpiar asignaturas impartidas existentes
    AsignaturaImpartida.objects.all().delete()
    Clase.objects.all().delete()
    print("🧹 Asignaturas impartidas y clases anteriores eliminadas")
    
    # Obtener todos los cursos
    cursos_objetivo = Curso.objects.all().order_by('nivel', 'letra')
    
    # Obtener asignaturas obligatorias por nivel
    asignaturas_por_nivel = obtener_asignaturas_obligatorias_por_nivel()
    
    # Obtener docentes por especialidad
    docentes_especialidad = obtener_docentes_por_especialidad()
    
    # Contador de asignaciones por asignatura
    asignaciones_por_asignatura = {}
    
    # Asignaciones existentes para control de conflictos
    asignaciones_existentes = []
    
    print(f"🎯 Iniciando asignación para cursos: {[f'{c.nivel}°{c.letra}' for c in cursos_objetivo]}")
    
    for curso in cursos_objetivo:
        print(f"\n📚 Procesando {curso}")
        
        # Obtener bloques disponibles para este curso específico
        bloques_disponibles = obtener_bloques_disponibles_por_curso(curso)
        
        # Obtener asignaturas para este nivel
        asignaturas_nivel = asignaturas_por_nivel[curso.nivel]
        
        # Inicializar contador para este curso
        if curso not in asignaciones_por_asignatura:
            asignaciones_por_asignatura[curso] = {}
        
        for asignatura in asignaturas_nivel:
            asignaciones_por_asignatura[curso][asignatura] = 0
        
        # Asignar cada asignatura
        for asignatura in asignaturas_nivel:
            print(f"  📖 Asignando {asignatura.nombre}")
            
            # Buscar docente disponible para esta asignatura
            docente_asignado = None
            for especialidad, docentes in docentes_especialidad.items():
                if verificar_especialidad_docente(asignatura.nombre, especialidad):
                    for docente in docentes:
                        # Verificar si este docente ya tiene muchas asignaciones
                        asignaciones_docente = sum(1 for a in asignaciones_existentes if a['docente'] == docente)
                        if asignaciones_docente < 25:  # Límite de asignaciones por docente
                            docente_asignado = docente
                            break
                    if docente_asignado:
                        break
            
            if not docente_asignado:
                print(f"    ⚠️ No se encontró docente disponible para {asignatura.nombre}")
                continue
            
            # Determinar cuántas veces debe aparecer esta asignatura en la semana
            # Basado en la importancia de la asignatura
            frecuencia_asignatura = {
                'Lenguaje': 3,  # 3 sesiones de 2 bloques = 6 bloques total
                'Matemáticas': 3,
                'Historia': 2,  # 2 sesiones de 2 bloques = 4 bloques total
                'Biología': 2,
                'Física': 2,
                'Química': 2,
                'Inglés': 2,
                'Educación Física': 2,
                'Arte': 2,      # 2 sesiones de 1 bloque = 2 bloques total
                'Música': 2,    # 2 sesiones de 1 bloque = 2 bloques total
                'Tecnología': 2,
                'Filosofía': 2,
            }
            
            frecuencia = frecuencia_asignatura.get(asignatura.nombre, 2)
            
            # Crear código único para la asignatura impartida
            codigo = f"{asignatura.nombre[:3].upper()}{curso.nivel}{curso.letra}"
            
            # Crear la asignatura impartida
            asignatura_impartida = AsignaturaImpartida.objects.create(
                asignatura=asignatura,
                docente=docente_asignado,
                codigo=codigo
            )
            
            # Determinar si la asignatura necesita 1 o 2 bloques consecutivos
            asignaturas_un_bloque = ['Arte', 'Música']
            necesita_dos_bloques = asignatura.nombre not in asignaturas_un_bloque
            
            # Asignar bloques para esta asignatura
            sesiones_asignadas = 0
            intentos_maximos = 100
            
            while sesiones_asignadas < frecuencia and intentos_maximos > 0:
                intentos_maximos -= 1
                
                # Seleccionar bloque aleatorio disponible
                bloques_disponibles_curso = [
                    (dia, bloque) for dia, bloque in bloques_disponibles
                    if not any(
                        a['curso'] == curso and a['dia'] == dia and a['bloque'] == bloque
                        for a in asignaciones_existentes
                    )
                ]
                
                if not bloques_disponibles_curso:
                    print(f"    ⚠️ No hay bloques disponibles para {asignatura.nombre}")
                    break
                
                dia, bloque_inicio = random.choice(bloques_disponibles_curso)
                
                # Verificar disponibilidad según si necesita 1 o 2 bloques
                if necesita_dos_bloques:
                    if not verificar_disponibilidad_bloques_consecutivos(dia, bloque_inicio, docente_asignado, curso, asignaciones_existentes):
                        continue
                else:
                    # Para asignaturas de 1 bloque, verificar solo el bloque actual
                    if not verificar_disponibilidad_docente(docente_asignado, dia, bloque_inicio, asignaciones_existentes):
                        continue
                
                # Verificar que no se repita la misma asignatura en el mismo día
                asignaciones_mismo_dia = [
                    a for a in asignaciones_existentes
                    if a['curso'] == curso and a['dia'] == dia and a['asignatura'] == asignatura
                ]
                
                if len(asignaciones_mismo_dia) >= 1:
                    continue
                
                # Crear las clases
                sala = asignar_sala_especial(asignatura)
                
                if necesita_dos_bloques:
                    # Crear dos clases consecutivas
                    for i in range(2):
                        bloque = str(int(bloque_inicio) + i)
                        clase = Clase.objects.create(
                            asignatura_impartida=asignatura_impartida,
                            curso=curso,
                            fecha=dia,
                            horario=bloque,
                            sala=sala
                        )
                        
                        # Registrar la asignación
                        asignaciones_existentes.append({
                            'curso': curso,
                            'asignatura': asignatura,
                            'docente': docente_asignado,
                            'dia': dia,
                            'bloque': bloque,
                            'sala': sala
                        })
                    
                    print(f"    ✅ {asignatura.nombre} - {docente_asignado.usuario.nombre} {docente_asignado.usuario.apellido_paterno} - {dia} {bloque_inicio}-{str(int(bloque_inicio)+1)} - {sala}")
                else:
                    # Crear una sola clase
                    clase = Clase.objects.create(
                        asignatura_impartida=asignatura_impartida,
                        curso=curso,
                        fecha=dia,
                        horario=bloque_inicio,
                        sala=sala
                    )
                    
                    # Registrar la asignación
                    asignaciones_existentes.append({
                        'curso': curso,
                        'asignatura': asignatura,
                        'docente': docente_asignado,
                        'dia': dia,
                        'bloque': bloque_inicio,
                        'sala': sala
                    })
                    
                    print(f"    ✅ {asignatura.nombre} - {docente_asignado.usuario.nombre} {docente_asignado.usuario.apellido_paterno} - {dia} {bloque_inicio} - {sala}")
                
                asignaciones_por_asignatura[curso][asignatura] += 1
                sesiones_asignadas += 1
    
    # Mostrar resumen
    print(f"\n📊 RESUMEN DE ASIGNACIONES:")
    for curso in cursos_objetivo:
        print(f"\n{curso}:")
        for asignatura, cantidad in asignaciones_por_asignatura[curso].items():
            print(f"  {asignatura.nombre}: {cantidad} sesiones")
    
    # Mostrar carga docente
    print(f"\n👨‍🏫 CARGA DOCENTE:")
    docentes_utilizados = {}
    for asignacion in asignaciones_existentes:
        docente = asignacion['docente']
        if docente not in docentes_utilizados:
            docentes_utilizados[docente] = 0
        docentes_utilizados[docente] += 1
    
    for docente, cantidad in sorted(docentes_utilizados.items(), key=lambda x: x[1], reverse=True):
        print(f"  {docente.usuario.nombre} {docente.usuario.apellido_paterno}: {cantidad} bloques")

if __name__ == "__main__":
    crear_asignaturas_impartidas_completas() 