import os
import django
import sys
import random

# Configuración de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import AsignaturaImpartida, Clase

def poblar_horarios_electivos():
    print("🧹 Limpiando horarios de clases electivas anteriores...")
    # Elimina solo las clases asociadas a asignaturas electivas para evitar duplicados
    Clase.objects.filter(asignatura_impartida__asignatura__es_electivo=True).delete()
    
    print("📚 Obteniendo electivos con profesor asignado...")
    electivos_impartidos = AsignaturaImpartida.objects.filter(asignatura__es_electivo=True).select_related('asignatura')

    if not electivos_impartidos.exists():
        print("⚠️ No hay asignaturas electivas impartidas para crear horarios. Finalizando.")
        return

    # Bloques y días disponibles para los electivos
    dias_semana = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES'] # Viernes tarde libre
    bloques_tarde = ['7', '8', '9']
    salas_disponibles = [sala[0] for sala in Clase.SALA_CHOICES if 'SALA' in sala[0]]

    # Barajamos los días para que la asignación sea variada en cada ejecución
    random.shuffle(dias_semana)
    
    print("🗓️ Creando horarios para los electivos en bloques 7, 8 y 9...")

    # Distribuir electivos en los días para evitar choques de horario
    # Esto es una simplificación, asume que no hay más electivos que cupos
    
    horarios_creados = 0
    # Asignamos un día y un bloque a cada electivo
    for i, impartida in enumerate(electivos_impartidos):
        # Asignar día de forma cíclica
        dia_asignado = dias_semana[i % len(dias_semana)]
        
        # Asignar sala aleatoria
        sala_asignada = random.choice(salas_disponibles)

        # Asignar a los 3 bloques de la tarde
        for bloque in bloques_tarde:
            Clase.objects.create(
                asignatura_impartida=impartida,
                curso=None,  # Los electivos no tienen un curso único
                fecha=dia_asignado,
                horario=bloque,
                sala=sala_asignada
            )
        
        horarios_creados += len(bloques_tarde)
        print(f"  ✅ Horario para '{impartida.asignatura.nombre}' creado el {dia_asignado} en sala {sala_asignada} (bloques 7, 8, 9)")

    print(f"\n🎉 ¡Proceso completado! Se han creado {horarios_creados} bloques de clase para los electivos.")

if __name__ == '__main__':
    poblar_horarios_electivos() 