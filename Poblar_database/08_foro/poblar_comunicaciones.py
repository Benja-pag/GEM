#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para poblar el sistema de comunicaciones con mensajes de ejemplo.
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Comunicacion, AdjuntoComunicacion, AuthUser, Curso

def poblar_comunicaciones():
    """
    Crea comunicaciones de ejemplo en el sistema.
    """
    print("🗑️ Limpiando comunicaciones anteriores...")
    Comunicacion.objects.all().delete()
    
    print("👥 Obteniendo usuarios y cursos...")
    usuarios = list(AuthUser.objects.all())
    cursos = list(Curso.objects.all())
    
    if not usuarios:
        print("❌ No hay usuarios en la base de datos. No se pueden crear comunicaciones.")
        return
    
    if not cursos:
        print("❌ No hay cursos en la base de datos. No se pueden crear comunicaciones.")
        return
    
    # Datos de ejemplo para las comunicaciones
    comunicaciones_ejemplo = [
        {
            'asunto': 'Información sobre Matrícula 2026',
            'contenido': """Estimados apoderados y estudiantes,

Junto con saludar, les informamos que el proceso de matrícula para el año académico 2026 comenzará el próximo lunes 15 de enero.

Documentos requeridos:
- Certificado de notas del año anterior
- Certificado de alumno regular
- Pago de matrícula
- Formulario de datos actualizados

La fecha límite para completar el proceso es el 31 de enero de 2026.

Para consultas, pueden contactar a la oficina de administración.

Saludos cordiales,
Dirección Académica""",
            'autor': usuarios[0] if usuarios else None,
            'destinatarios_cursos': cursos[:3],  # Primeros 3 cursos
            'fecha': datetime.now() - timedelta(days=2)
        },
        {
            'asunto': 'Autorización Salida Pedagógica - Museo de Historia Natural',
            'contenido': """Estimados apoderados y estudiantes del 3°A,

Junto con saludar, les informamos que el próximo viernes 20 de enero realizaremos una salida pedagógica al Museo de Historia Natural.

Detalles de la salida:
- Fecha: Viernes 20 de enero de 2026
- Hora de salida: 8:30 AM
- Hora de regreso: 2:30 PM
- Lugar: Museo de Historia Natural
- Costo: $5.000 por estudiante

Es obligatorio que cada estudiante traiga la autorización firmada por su apoderado. Sin este documento, no podrá participar de la actividad.

La fecha límite para entregar la autorización es este miércoles 18 de enero.

Saludos cordiales,
Prof. Jefe: C. Bravo""",
            'autor': usuarios[1] if len(usuarios) > 1 else usuarios[0],
            'destinatarios_cursos': [cursos[2]] if len(cursos) > 2 else cursos[:1],  # Solo 3°A
            'fecha': datetime.now() - timedelta(days=1)
        },
        {
            'asunto': 'Recordatorio: Reunión de Apoderados',
            'contenido': """Estimados apoderados,

Les recordamos que este jueves 19 de enero a las 19:00 horas se realizará la reunión de apoderados correspondiente al mes de enero.

Temas a tratar:
- Información general del curso
- Calendario de evaluaciones
- Actividades programadas
- Consultas y sugerencias

La reunión se llevará a cabo en la sala de clases de cada curso.

Esperamos contar con su presencia.

Saludos cordiales,
Equipo Directivo""",
            'autor': usuarios[0] if usuarios else None,
            'destinatarios_cursos': cursos,
            'fecha': datetime.now() - timedelta(hours=6)
        },
        {
            'asunto': 'Cambio de Horario - Clases de Educación Física',
            'contenido': """Estimados estudiantes,

Les informamos que debido a las condiciones climáticas, las clases de Educación Física programadas para mañana se realizarán en el gimnasio cubierto en lugar del patio.

Los horarios se mantienen igual, solo cambia el lugar de realización.

Disculpen las molestias ocasionadas.

Saludos cordiales,
Departamento de Educación Física""",
            'autor': usuarios[2] if len(usuarios) > 2 else usuarios[0],
            'destinatarios_cursos': cursos[1:4] if len(cursos) > 3 else cursos,
            'fecha': datetime.now() - timedelta(hours=2)
        },
        {
            'asunto': 'Convocatoria: Taller de Robótica',
            'contenido': """Estimados estudiantes interesados en la tecnología,

Les invitamos a participar del taller de robótica que se realizará todos los martes y jueves de 15:30 a 17:00 horas.

El taller está dirigido a estudiantes de 7° a 4° medio y no tiene costo adicional.

Inscripciones abiertas hasta el viernes 22 de enero.

Para más información, consultar con el profesor de Tecnología.

¡Los esperamos!

Saludos cordiales,
Departamento de Tecnología""",
            'autor': usuarios[3] if len(usuarios) > 3 else usuarios[0],
            'destinatarios_cursos': cursos[3:] if len(cursos) > 3 else cursos,
            'fecha': datetime.now() - timedelta(hours=1)
        }
    ]
    
    print("📝 Creando comunicaciones...")
    comunicaciones_creadas = []
    
    for i, datos in enumerate(comunicaciones_ejemplo, 1):
        if not datos['autor']:
            continue
            
        comunicacion = Comunicacion.objects.create(
            asunto=datos['asunto'],
            contenido=datos['contenido'],
            autor=datos['autor'],
            fecha_envio=datos['fecha']
        )
        
        # Agregar destinatarios por curso
        for curso in datos['destinatarios_cursos']:
            comunicacion.destinatarios_cursos.add(curso)
        
        comunicaciones_creadas.append(comunicacion)
        print(f"✅ Comunicación {i}: {datos['asunto']}")
    
    print(f"\n🎉 Se crearon {len(comunicaciones_creadas)} comunicaciones de ejemplo.")
    print("📊 Resumen:")
    for comunicacion in comunicaciones_creadas:
        destinatarios = ", ".join([str(curso) for curso in comunicacion.destinatarios_cursos.all()])
        print(f"   - '{comunicacion.asunto}' -> {destinatarios}")

if __name__ == "__main__":
    poblar_comunicaciones() 