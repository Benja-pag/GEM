import os
import django
import sys
from datetime import date, time
from collections import defaultdict
import random
from collections import Counter

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
    """Obtiene las asignaturas correspondientes al nivel."""
    if nivel in [1, 2]:
        return Asignatura.objects.filter(
            nombre__in=['Matemáticas', 'Lenguaje', 'Historia', 'Biología', 'Física', 'Química', 'Inglés', 'Educación Física', 'Arte', 'Música', 'Tecnología']
        ).exclude(nombre__in=['Filosofía'])
    else:
        return Asignatura.objects.filter(
            nombre__in=['Matemáticas', 'Lenguaje', 'Historia', 'Biología', 'Física', 'Química', 'Inglés', 'Educación Física', 'Filosofía']
        ).exclude(nombre__in=['Arte', 'Música', 'Tecnología'])

def obtener_docente_por_especialidad(asignatura, docentes_por_asignatura, docentes_ocupados):
    """Obtiene un docente según la especialidad de la asignatura."""
    if asignatura.nombre in docentes_por_asignatura:
        return docentes_por_asignatura[asignatura.nombre]
    
    # Mapeo de asignaturas obligatorias a especialidades (nombres exactos de la BD)
    mapeo_obligatorias = {
        'Matemáticas': ['Matematicas'],
        'Lenguaje': ['Lenguaje'],
        'Historia': ['Historia'],
        'Biología': ['Biologia'],
        'Física': ['Fisica'],
        'Química': ['Quimica'],
        'Educación Física': ['Educación Fisica'],
        'Arte': ['Arte'],
        'Música': ['Música y Composición'],
        'Filosofía': ['Filosofía y Ética']
    }
    
    # Mapeo de electivos que pueden dar asignaturas obligatorias relacionadas
    mapeo_electivos = {
        'Matemáticas Aplicadas': ['Matematicas', 'Fisica'],
        'Literatura Avanzada': ['Lenguaje', 'Historia'],
        'Historia del Arte': ['Historia', 'Arte'],
        'Biología Molecular': ['Biologia', 'Quimica'],
        'Física Cuántica': ['Fisica', 'Matematicas'],
        'Química Orgánica': ['Quimica', 'Biologia']
    }
    
    # Primero buscar docentes con la especialidad exacta
    especialidades_buscadas = mapeo_obligatorias.get(asignatura.nombre, [asignatura.nombre])
    
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
    
    # Si no hay docentes con especialidad exacta, buscar docentes de electivos relacionados
    especialidades_relacionadas = []
    for electivo, especialidades in mapeo_electivos.items():
        if asignatura.nombre in especialidades:
            especialidades_relacionadas.extend(mapeo_electivos[electivo])
    
    if especialidades_relacionadas:
        docentes_electivos = []
        for docente in Docente.objects.all():
            if docente.especialidad and docente.especialidad.nombre in especialidades_relacionadas:
                # Solo considerar docentes de electivos (no de asignaturas obligatorias)
                if docente.especialidad.nombre not in [esp for sublist in mapeo_obligatorias.values() for esp in sublist]:
                    if docente not in docentes_ocupados:
                        docentes_electivos.append(docente)
        
        if docentes_electivos:
            docente_elegido = random.choice(docentes_electivos)
            docentes_por_asignatura[asignatura.nombre] = docente_elegido
            docentes_ocupados.add(docente_elegido)
            return docente_elegido
    
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
        # 3° y 4° Medio: solo bloques 1-6 (mañana), bloques 7-9 reservados para electivos
        estructura_bloques = {
            'LUNES': ['1-2', '3-4', '5-6'],
            'MARTES': ['1-2', '3-4', '5-6'],
            'MIERCOLES': ['1-2', '3-4', '5-6'],
            'JUEVES': ['1-2', '3-4', '5-6'],
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
    
    # Frecuencias objetivo ajustadas para asegurar cobertura completa
    if curso.nivel in [1, 2]:
        frecuencias = {
            'Matemáticas': 4, 'Lenguaje': 4, 'Historia': 3, 'Biología': 2,
            'Física': 2, 'Química': 2, 'Inglés': 3, 'Educación Física': 2, 
            'Arte': 2, 'Música': 2, 'Tecnología': 2
        }
    else:
        frecuencias = {
            'Matemáticas': 4, 'Lenguaje': 4, 'Historia': 3, 'Biología': 2,
            'Física': 2, 'Química': 2, 'Inglés': 3, 'Educación Física': 2,
            'Filosofía': 2
        }
    
    # Asignar asignaturas regulares (pares de bloques) - ALEATORIZAR ORDEN
    asignaturas_regulares = [a for a in asignaturas if not es_asignatura_especial(a)]
    random.shuffle(asignaturas_regulares)  # Aleatorizar orden de asignaturas
    
    # Asignar TODAS las asignaturas regulares con frecuencias controladas
    for asignatura in asignaturas_regulares:
        asignar_asignatura_regular(asignatura, curso, frecuencias, horario_curso, 
                                 asignaturas_asignadas, asignaturas_impartidas, 
                                 docentes_por_asignatura, docentes_ocupados, estructura_bloques)
    
    # Asignar asignaturas especiales
    asignaturas_especiales = [a for a in asignaturas if es_asignatura_especial(a)]
    random.shuffle(asignaturas_especiales)
    
    for asignatura in asignaturas_especiales:
        asignar_asignatura_especial(asignatura, curso, frecuencias, horario_curso, 
                                  asignaturas_asignadas, asignaturas_impartidas, 
                                  docentes_por_asignatura, docentes_ocupados, estructura_bloques)
    
    print(f"  📊 Asignaturas asignadas: {dict(asignaturas_asignadas)}")

def asignar_asignatura_regular(asignatura, curso, frecuencias, horario_curso, 
                              asignaturas_asignadas, asignaturas_impartidas, 
                              docentes_por_asignatura, docentes_ocupados, estructura_bloques):
    """Asigna una asignatura regular en pares de bloques."""
    # Reiniciar docentes ocupados para esta asignatura específica
    docentes_ocupados_asignatura = set()
    
    pares_asignados = 0
    max_intentos = 200  # Aumentar intentos para asegurar asignación
    codigo = f"{asignatura.nombre[:3].upper()}{curso.nivel}{curso.letra}"
    
    frecuencia_objetivo = frecuencias.get(asignatura.nombre, 2)
    
    while pares_asignados < frecuencia_objetivo and max_intentos > 0:
        # Obtener docente para esta asignación específica
        docente = obtener_docente_por_especialidad(asignatura, docentes_por_asignatura, docentes_ocupados_asignatura)
        
        if asignatura.nombre not in asignaturas_impartidas:
            asignatura_imp, _ = AsignaturaImpartida.objects.get_or_create(
                asignatura=asignatura, docente=docente, codigo=codigo
            )
            asignaturas_impartidas[asignatura.nombre] = asignatura_imp
        else:
            asignatura_imp = asignaturas_impartidas[asignatura.nombre]
        
        asignacion_exitosa = False
        dias_disponibles = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
        random.shuffle(dias_disponibles)
        
        for dia in dias_disponibles:
            if asignacion_exitosa:
                break
            
            # Verificar que la asignatura no se repita más de una vez por día
            if dia in horario_curso:
                asignaturas_en_dia = [v for v in horario_curso[dia].values()]
                if asignatura.nombre in asignaturas_en_dia:
                    continue
            
            # Buscar bloques disponibles
            bloques_disponibles = [bg for bg in estructura_bloques[dia] if bg in ['1-2', '3-4', '5-6', '7-8']]
            random.shuffle(bloques_disponibles)
            
            for bloque_grupo in bloques_disponibles:
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
    
    # Si no se pudo asignar la frecuencia completa, mostrar advertencia
    if pares_asignados < frecuencia_objetivo:
        print(f"  ⚠️ {asignatura.nombre}: asignado {pares_asignados}/{frecuencia_objetivo} veces")

def asignar_asignatura_especial(asignatura, curso, frecuencias, horario_curso, 
                               asignaturas_asignadas, asignaturas_impartidas, 
                               docentes_por_asignatura, docentes_ocupados, estructura_bloques):
    """Asigna una asignatura especial en bloques individuales."""
    docente = obtener_docente_por_especialidad(asignatura, docentes_por_asignatura, docentes_ocupados)
    bloques_asignados = 0
    max_intentos = 50
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
        dias_especiales = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES']
        random.shuffle(dias_especiales)
        
        for dia in dias_especiales:
            if asignacion_exitosa:
                break
            
            # Verificar que la asignatura no se repita más de una vez por día
            if dia in horario_curso:
                asignaturas_en_dia = [v for v in horario_curso[dia].values()]
                if asignatura.nombre in asignaturas_en_dia:
                    continue
            
            # Para 3° y 4° medio, usar solo bloque 5 (no interfiere con pares)
            # Para 1° y 2° medio, usar bloque 9
            if curso.nivel in [3, 4]:
                bloques_individuales = ['5']  # Solo bloque 5 para no romper pares
            else:
                bloques_individuales = ['9']  # Solo bloque 9 para 1° y 2° medio
            
            for bloque_grupo in bloques_individuales:
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

def mostrar_resumen_asignaturas():
    """Muestra un resumen de cuántas veces aparece cada asignatura en todos los horarios."""
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE ASIGNATURAS EN HORARIOS GENERADOS")
    print("=" * 80)
    
    # Contar todas las clases por asignatura
    contador_asignaturas = Counter()
    
    for clase in Clase.objects.all().select_related('asignatura_impartida__asignatura'):
        nombre_asignatura = clase.asignatura_impartida.asignatura.nombre
        contador_asignaturas[nombre_asignatura] += 1
    
    # Mostrar resultados ordenados por cantidad
    if contador_asignaturas:
        print("\n🎯 TOTAL DE REPETICIONES POR ASIGNATURA:")
        print("-" * 50)
        for asignatura, cantidad in contador_asignaturas.most_common():
            print(f"  • {asignatura}: {cantidad} veces")
        
        print(f"\n📈 TOTAL DE CLASES GENERADAS: {sum(contador_asignaturas.values())}")
        print(f"📚 TOTAL DE ASIGNATURAS DIFERENTES: {len(contador_asignaturas)}")
    else:
        print("  ⚠️  No hay clases registradas")

def poblar_horarios_v3():
    """Pobla los horarios cumpliendo todas las reglas específicas."""
    print("🧹 Borrando clases y asignaturas impartidas...")
    Clase.objects.all().delete()
    AsignaturaImpartida.objects.all().delete()
    
    print("🎯 Generando horarios según reglas específicas...")
    
    cursos = Curso.objects.all().order_by('nivel', 'letra')
    
    for curso in cursos:
        generar_horario_curso(curso)
    
    # Mostrar resumen de asignaturas
    mostrar_resumen_asignaturas()
    
    print("\n✅ Poblamiento de horarios V3 completado.")
    print("🔍 Ejecuta 'python Poblar_database\\06_verificacion\\verificar_horario.py' para verificar los resultados.")

if __name__ == "__main__":
    poblar_horarios_v3() 