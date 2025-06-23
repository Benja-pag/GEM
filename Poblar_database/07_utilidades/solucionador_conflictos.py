import os
import django
import sys
from datetime import date, time

# Agrega el directorio raíz del proyecto al path (sube dos niveles desde subcarpeta)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from itertools import product

from Core.models import (
    Clase, AsignaturaImpartida, Curso, Docente
)

def obtener_horarios_disponibles(dia, docente, sala, curso):
    """
    Obtiene los horarios disponibles para una combinación de día, docente, sala y curso
    """
    # Todos los horarios posibles
    todos_horarios = set(['1', '2', '3', '4', '5', '6', '7', '8', '9'])
    
    # Si es viernes, solo horarios hasta el 6
    if dia == 'VIERNES':
        todos_horarios = set(['1', '2', '3', '4', '5', '6'])

    # Obtener horarios ocupados por el docente
    horarios_docente = set(Clase.objects.filter(
        asignatura_impartida__docente=docente,
        fecha=dia
    ).values_list('horario', flat=True))

    # Obtener horarios ocupados en la sala (solo para salas especiales)
    horarios_sala = set()
    if sala in ['GIMNASIO', 'LAB_BIO', 'LAB_QUI', 'LAB_FIS', 'SALA_9', 'SALA_10']:
        horarios_sala = set(Clase.objects.filter(
            fecha=dia,
            sala=sala
        ).values_list('horario', flat=True))

    # Obtener horarios ocupados por el curso
    horarios_curso = set(Clase.objects.filter(
        curso=curso,
        fecha=dia
    ).values_list('horario', flat=True))

    # Restar todos los horarios ocupados
    horarios_disponibles = todos_horarios - horarios_docente - horarios_sala - horarios_curso

    return sorted(list(horarios_disponibles))

def resolver_conflicto_clase(clase):
    """
    Intenta resolver el conflicto de una clase buscando un nuevo horario
    """
    docente = clase.asignatura_impartida.docente
    sala = clase.sala
    curso = clase.curso
    dia = clase.fecha
    
    # Obtener horarios disponibles
    horarios_disponibles = obtener_horarios_disponibles(dia, docente, sala, curso)
    
    if horarios_disponibles:
        # Tomar el primer horario disponible
        nuevo_horario = horarios_disponibles[0]
        print(f"Resolviendo conflicto para {clase.asignatura_impartida.codigo}:")
        print(f"  - Cambiando de horario {clase.horario} a {nuevo_horario} en {dia}")
        clase.horario = nuevo_horario
        clase.save()
        return True
    
    # Si no hay horarios disponibles en el mismo día, intentar otro día
    dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
    dias.remove(dia)
    
    for nuevo_dia in dias:
        horarios_disponibles = obtener_horarios_disponibles(nuevo_dia, docente, sala, curso)
        if horarios_disponibles:
            nuevo_horario = horarios_disponibles[0]
            print(f"Resolviendo conflicto para {clase.asignatura_impartida.codigo}:")
            print(f"  - Cambiando de {dia} horario {clase.horario} a {nuevo_dia} horario {nuevo_horario}")
            clase.fecha = nuevo_dia
            clase.horario = nuevo_horario
            clase.save()
            return True
    
    return False

def resolver_todos_conflictos():
    """
    Intenta resolver todos los conflictos de horarios existentes
    """
    # Obtener todas las clases
    clases = Clase.objects.all()
    conflictos_resueltos = 0
    conflictos_no_resueltos = 0

    for clase in clases:
        docente = clase.asignatura_impartida.docente
        sala = clase.sala
        curso = clase.curso
        dia = clase.fecha
        horario = clase.horario

        # Verificar si hay conflicto
        conflicto_docente = Clase.objects.filter(
            asignatura_impartida__docente=docente,
            fecha=dia,
            horario=horario
        ).exclude(id=clase.id).exists()

        conflicto_sala = False
        if sala in ['GIMNASIO', 'LAB_BIO', 'LAB_QUI', 'LAB_FIS', 'SALA_9', 'SALA_10']:
            conflicto_sala = Clase.objects.filter(
                fecha=dia,
                horario=horario,
                sala=sala
            ).exclude(id=clase.id).exists()

        conflicto_curso = Clase.objects.filter(
            curso=curso,
            fecha=dia,
            horario=horario
        ).exclude(id=clase.id).exists()

        if conflicto_docente or conflicto_sala or conflicto_curso:
            if resolver_conflicto_clase(clase):
                conflictos_resueltos += 1
            else:
                conflictos_no_resueltos += 1
                print(f"⚠️ No se pudo resolver el conflicto para {clase.asignatura_impartida.codigo}")

    print(f"\nResumen de resolución de conflictos:")
    print(f"- Conflictos resueltos: {conflictos_resueltos}")
    print(f"- Conflictos no resueltos: {conflictos_no_resueltos}")

if __name__ == "__main__":
    print("Iniciando resolución de conflictos...")
    resolver_todos_conflictos()
    print("Proceso completado.") 