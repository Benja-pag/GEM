import os
import django
import sys
import random
from collections import defaultdict
from itertools import product

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura el módulo de settings
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

def es_asignatura_especial(asignatura):
    """Determina si una asignatura puede ocupar solo 1 bloque"""
    asignaturas_especiales = ['Música', 'Arte', 'Filosofía', 'Educación Física']
    return asignatura.nombre in asignaturas_especiales

def crear_horarios_unicos_por_nivel():
    """
    Crea horarios únicos para cada curso, garantizando que no haya conflictos
    entre cursos del mismo nivel
    """
    print("🧹 Limpiando datos antiguos...")
    AsignaturaImpartida.objects.all().delete()
    Clase.objects.all().delete()
    
    print("📚 Obteniendo datos necesarios...")
    cursos_objetivo = list(Curso.objects.all().order_by('nivel', 'letra'))
    asignaturas_por_nivel = obtener_asignaturas_obligatorias_por_nivel()
    docentes_especialidad = obtener_docentes_por_especialidad()
    
    # Estructuras de datos para el proceso
    asignaciones_existentes = []
    frecuencia_asignatura_doble = {
        'Lenguaje': 3, 'Matemáticas': 3, 'Historia': 2, 'Biología': 2,
        'Física': 2, 'Química': 2, 'Inglés': 2, 'Tecnología': 2
    }
    frecuencia_asignatura_simple = {
        'Educación Física': 2, 'Arte': 2, 'Música': 2, 'Filosofía': 2
    }
    sesiones_asignadas = defaultdict(lambda: defaultdict(int))
    
    # Agrupar cursos por nivel
    cursos_por_nivel = defaultdict(list)
    for curso in cursos_objetivo:
        cursos_por_nivel[curso.nivel].append(curso)
    
    print("\n🎯 ASIGNANDO HORARIOS ÚNICOS POR NIVEL")
    print("="*60)
    
    for nivel, cursos in cursos_por_nivel.items():
        print(f"\n📚 Procesando nivel {nivel}°: {', '.join([str(curso) for curso in cursos])}")
        
        # Pre-asignar docentes para cada curso
        docentes_asignados_a_materia = {}
        for curso in cursos:
            print(f"  Asignando docentes para {curso}...")
            for asignatura in asignaturas_por_nivel[nivel]:
                docentes_potenciales = [
                    d for esp, docs in docentes_especialidad.items() 
                    if verificar_especialidad_docente(asignatura.nombre, esp) 
                    for d in docs
                ]
                if not docentes_potenciales:
                    print(f"    ⚠️ No hay docentes para {asignatura.nombre}")
                    continue
                
                # Seleccionar docente aleatoriamente
                docente_elegido = random.choice(docentes_potenciales)
                docentes_asignados_a_materia[(curso, asignatura)] = docente_elegido
                print(f"    ✓ {asignatura.nombre:<20} -> {docente_elegido.usuario.nombre} {docente_elegido.usuario.apellido_paterno}")
        
        # Crear horarios únicos para cada curso del nivel
        for curso in cursos:
            print(f"\n  🎯 Creando horario único para {curso}...")
            
            # Obtener bloques disponibles para este curso
            bloques_disponibles = obtener_bloques_disponibles_por_curso(curso)
            
            # MEJORA: Ordenar asignaturas por prioridad (más frecuencias primero)
            asignaturas_regulares = [a for a in asignaturas_por_nivel[nivel] if not es_asignatura_especial(a)]
            asignaturas_especiales = [a for a in asignaturas_por_nivel[nivel] if es_asignatura_especial(a)]
            
            # Ordenar por frecuencia (mayor a menor)
            asignaturas_regulares.sort(key=lambda a: frecuencia_asignatura_doble.get(a.nombre, 0), reverse=True)
            asignaturas_especiales.sort(key=lambda a: frecuencia_asignatura_simple.get(a.nombre, 0), reverse=True)
            
            # MEJORA: Intentar múltiples veces con diferentes configuraciones
            max_intentos = 3
            mejor_resultado = 0
            
            for intento in range(max_intentos):
                print(f"    🔄 Intento {intento + 1}/{max_intentos}")
                
                # Limpiar datos del intento anterior
                if intento > 0:
                    # Eliminar solo las clases de este curso
                    Clase.objects.filter(curso=curso).delete()
                    AsignaturaImpartida.objects.filter(clases__curso=curso).delete()
                    # Limpiar asignaciones existentes de este curso
                    asignaciones_existentes = [a for a in asignaciones_existentes if a['curso'] != curso]
                    sesiones_asignadas[curso].clear()
                
                # Mezclar bloques disponibles
                bloques_curso = bloques_disponibles.copy()
                random.shuffle(bloques_curso)
                
                # Asignar asignaturas regulares (bloques dobles)
                for asignatura in asignaturas_regulares:
                    frecuencia = frecuencia_asignatura_doble.get(asignatura.nombre, 0)
                    docente_asignado = docentes_asignados_a_materia.get((curso, asignatura))
                    
                    if not docente_asignado:
                        continue
                    
                    # Continuar asignando hasta completar la frecuencia requerida
                    while sesiones_asignadas[curso][asignatura] < frecuencia and len(bloques_curso) >= 2:
                        # Buscar bloques consecutivos disponibles
                        asignacion_exitosa = False
                        for i in range(len(bloques_curso) - 1):
                            dia, bloque_inicio = bloques_curso[i]
                            bloque_siguiente = str(int(bloque_inicio) + 1)
                            
                            # Verificar si el siguiente bloque está disponible
                            siguiente_disponible = False
                            for j in range(i + 1, len(bloques_curso)):
                                if (bloques_curso[j][0] == dia and 
                                    bloques_curso[j][1] == bloque_siguiente):
                                    siguiente_disponible = True
                                    break
                            
                            if not siguiente_disponible:
                                continue
                            
                            # Verificar conflictos
                            conflicto_encontrado = False
                            for asignacion in asignaciones_existentes:
                                if (asignacion['docente'] == docente_asignado and 
                                    asignacion['dia'] == dia and 
                                    asignacion['bloque'] in [bloque_inicio, bloque_siguiente]):
                                    conflicto_encontrado = True
                                    break
                            
                            if not conflicto_encontrado:
                                # Crear asignatura impartida y clases
                                codigo = f"{asignatura.nombre[:3].upper()}{curso.nivel}{curso.letra}"
                                asignatura_impartida, _ = AsignaturaImpartida.objects.get_or_create(
                                    asignatura=asignatura, docente=docente_asignado, codigo=codigo
                                )
                                
                                sala = asignar_sala_especial(asignatura)
                                
                                # Crear clases para ambos bloques
                                for bloque in [bloque_inicio, bloque_siguiente]:
                                    Clase.objects.create(
                                        asignatura_impartida=asignatura_impartida,
                                        curso=curso,
                                        fecha=dia,
                                        horario=bloque,
                                        sala=sala
                                    )
                                    asignaciones_existentes.append({
                                        'curso': curso,
                                        'asignatura': asignatura,
                                        'docente': docente_asignado,
                                        'dia': dia,
                                        'bloque': bloque,
                                        'sala': sala
                                    })
                                
                                # Remover bloques usados
                                bloques_curso = [b for b in bloques_curso 
                                               if not (b[0] == dia and b[1] in [bloque_inicio, bloque_siguiente])]
                                
                                sesiones_asignadas[curso][asignatura] += 1
                                print(f"      ✅ {asignatura.nombre} en {dia} bloques {bloque_inicio}-{bloque_siguiente}")
                                asignacion_exitosa = True
                                break
                        
                        if not asignacion_exitosa:
                            break  # No se pueden asignar más bloques consecutivos
                
                # Asignar asignaturas especiales (bloques simples)
                for asignatura in asignaturas_especiales:
                    frecuencia = frecuencia_asignatura_simple.get(asignatura.nombre, 0)
                    docente_asignado = docentes_asignados_a_materia.get((curso, asignatura))
                    
                    if not docente_asignado:
                        continue
                    
                    while sesiones_asignadas[curso][asignatura] < frecuencia and bloques_curso:
                        # Tomar el primer bloque disponible
                        dia, bloque = bloques_curso[0]
                        
                        # Verificar conflictos
                        conflicto_encontrado = False
                        for asignacion in asignaciones_existentes:
                            if (asignacion['docente'] == docente_asignado and 
                                asignacion['dia'] == dia and 
                                asignacion['bloque'] == bloque):
                                conflicto_encontrado = True
                                break
                        
                        if not conflicto_encontrado:
                            # Crear asignatura impartida y clase
                            codigo = f"{asignatura.nombre[:3].upper()}{curso.nivel}{curso.letra}"
                            asignatura_impartida, _ = AsignaturaImpartida.objects.get_or_create(
                                asignatura=asignatura, docente=docente_asignado, codigo=codigo
                            )
                            
                            sala = asignar_sala_especial(asignatura)
                            
                            Clase.objects.create(
                                asignatura_impartida=asignatura_impartida,
                                curso=curso,
                                fecha=dia,
                                horario=bloque,
                                sala=sala
                            )
                            
                            asignaciones_existentes.append({
                                'curso': curso,
                                'asignatura': asignatura,
                                'docente': docente_asignado,
                                'dia': dia,
                                'bloque': bloque,
                                'sala': sala
                            })
                            
                            sesiones_asignadas[curso][asignatura] += 1
                            print(f"      ✅ {asignatura.nombre} en {dia} bloque {bloque}")
                        
                        # Remover el bloque procesado
                        bloques_curso.pop(0)
                
                # Calcular resultado del intento
                total_asignado = sum(sesiones_asignadas[curso].values())
                if total_asignado > mejor_resultado:
                    mejor_resultado = total_asignado
                    print(f"    🎯 Mejor resultado hasta ahora: {total_asignado} sesiones")
                
                # Si completamos todas las asignaturas, salir del bucle
                asignaturas_completas = 0
                for asignatura in asignaturas_por_nivel[nivel]:
                    frecuencia_requerida = (frecuencia_asignatura_doble.get(asignatura.nombre, 0) or 
                                           frecuencia_asignatura_simple.get(asignatura.nombre, 0))
                    if sesiones_asignadas[curso][asignatura] >= frecuencia_requerida:
                        asignaturas_completas += 1
                
                if asignaturas_completas == len(asignaturas_por_nivel[nivel]):
                    print(f"    🎉 ¡Todas las asignaturas completadas en intento {intento + 1}!")
                    break
    
    # Resumen final
    print(f"\n📊 RESUMEN DE ASIGNACIÓN:")
    print("="*60)
    
    for nivel, cursos in cursos_por_nivel.items():
        print(f"\n🎓 NIVEL {nivel}°:")
        for curso in cursos:
            print(f"\n  {curso}:")
            asignaturas_obligatorias = asignaturas_por_nivel[nivel]
            for asignatura in sorted(asignaturas_obligatorias, key=lambda a: a.nombre):
                frecuencia_requerida = (frecuencia_asignatura_doble.get(asignatura.nombre, 0) or 
                                       frecuencia_asignatura_simple.get(asignatura.nombre, 0))
                cantidad_asignada = sesiones_asignadas[curso][asignatura]
                docente = docentes_asignados_a_materia.get((curso, asignatura))
                docente_nombre = f"{docente.usuario.nombre} {docente.usuario.apellido_paterno}" if docente else "N/A"
                estado = "✅ Cumple" if cantidad_asignada >= frecuencia_requerida else f"❌ Faltan {frecuencia_requerida - cantidad_asignada}"
                print(f"    - {asignatura.nombre:<20} | {docente_nombre:<25} | {cantidad_asignada}/{frecuencia_requerida} | {estado}")
    
    print(f"\n✅ Proceso completado exitosamente!")
    print(f"📈 Total de asignaturas impartidas creadas: {AsignaturaImpartida.objects.count()}")
    print(f"📈 Total de clases creadas: {Clase.objects.count()}")

if __name__ == "__main__":
    crear_horarios_unicos_por_nivel() 