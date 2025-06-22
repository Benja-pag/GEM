import os
import django
import sys
from collections import defaultdict

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Curso, Clase, Asignatura

def es_asignatura_especial(asignatura):
    """Determina si una asignatura puede ocupar solo 1 bloque."""
    asignaturas_especiales = ['Música', 'Arte', 'Filosofía', 'Educación Física']
    return asignatura.nombre in asignaturas_especiales

def verificar_horarios():
    """
    Verifica que todos los horarios de los cursos cumplan con las reglas de asignación:
    1. Las asignaturas regulares deben estar en bloques de 2 horas.
    2. Las asignaturas especiales (1 hora) no pueden estar aisladas.
    3. El día debe comenzar siempre con una asignatura de 2 bloques.
    """
    print("🔍 Iniciando verificación de horarios en la base de datos...")
    errores_encontrados = 0
    
    cursos = Curso.objects.all().order_by('nivel', 'letra')
    
    for curso in cursos:
        print(f"\nVerificando horario para el curso: {curso}")
        
        # Obtener todas las clases para este curso y agruparlas por día
        clases_curso = Clase.objects.filter(curso=curso).order_by('fecha', 'horario')
        horario_por_dia = defaultdict(list)
        
        for clase in clases_curso:
            # Convertir el número de bloque a entero para facilitar la lógica
            try:
                horario_por_dia[clase.fecha].append(clase)
            except ValueError:
                print(f"  ⚠️ Advertencia: El bloque '{clase.horario}' no es un número válido para la clase ID {clase.id}. Omitiendo.")
                continue

        # Verificar las reglas para cada día
        for dia, clases_del_dia in horario_por_dia.items():
            if not clases_del_dia:
                continue

            # Ordenar clases por el número de bloque
            clases_del_dia.sort(key=lambda c: int(c.horario))
            bloques_en_dia = {int(c.horario): c for c in clases_del_dia}
            bloques_ordenados = sorted(bloques_en_dia.keys())

            # REGLA 3: El día debe comenzar con una asignatura de 2 bloques
            if bloques_ordenados:
                primera_clase = bloques_en_dia[bloques_ordenados[0]]
                primera_asignatura = primera_clase.asignatura_impartida.asignatura
                if es_asignatura_especial(primera_asignatura):
                    print(f"  ❌ ERROR [Regla 3]: El día {dia} comienza con una asignatura especial de 1 bloque ('{primera_asignatura.nombre}' en bloque {bloques_ordenados[0]}).")
                    errores_encontrados += 1

            bloques_verificados = set()
            for bloque_num in bloques_ordenados:
                if bloque_num in bloques_verificados:
                    continue

                clase_actual = bloques_en_dia[bloque_num]
                asignatura = clase_actual.asignatura_impartida.asignatura

                if not es_asignatura_especial(asignatura):
                    # REGLA 1: Asignatura regular debe tener un par
                    bloque_siguiente = bloque_num + 1
                    if bloque_siguiente not in bloques_en_dia or bloques_en_dia[bloque_siguiente].asignatura_impartida.asignatura != asignatura:
                        print(f"  ❌ ERROR [Regla 1]: La asignatura regular '{asignatura.nombre}' en día {dia}, bloque {bloque_num}, no tiene un par consecutivo.")
                        errores_encontrados += 1
                    else:
                        bloques_verificados.add(bloque_num)
                        bloques_verificados.add(bloque_siguiente)
                else:
                    # REGLA 2: Asignatura especial no puede estar aislada
                    tiene_bloque_anterior = (bloque_num - 1) in bloques_en_dia
                    tiene_bloque_siguiente = (bloque_num + 1) in bloques_en_dia
                    
                    if not tiene_bloque_anterior and not tiene_bloque_siguiente:
                        print(f"  ❌ ERROR [Regla 2]: La asignatura especial '{asignatura.nombre}' está aislada en día {dia}, bloque {bloque_num}.")
                        errores_encontrados += 1
                    
                    bloques_verificados.add(bloque_num)

    if errores_encontrados == 0:
        print("\n✅ ¡Verificación completada! Todos los horarios cumplen con las reglas.")
    else:
        print(f"\n🚨 ¡Verificación completada! Se encontraron {errores_encontrados} errores en los horarios.")

if __name__ == "__main__":
    verificar_horarios() 