import os
import django
import sys
import json
from datetime import date, time
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Docente, CalendarioClase, CalendarioColegio, Asignatura, AsignaturaImpartida

print("=== TESTE DE CREACIÓN DE EVENTOS ===")

# Obtener Juan Pérez
docente = Docente.objects.get(usuario__nombre='Juan', usuario__apellido_paterno='Perez')
print(f'Juan Pérez ID: {docente.pk}')

# Obtener sus asignaturas
asignaturas = AsignaturaImpartida.objects.filter(docente=docente)
print(f'Asignaturas de Juan: {asignaturas.count()}')
for a in asignaturas:
    print(f'- {a.asignatura.nombre}')
    print(f'  AsignaturaImpartida ID: {a.id}')
    print(f'  Asignatura ID: {a.asignatura.id}')

# Crear evento de evaluación
asignatura_id = asignaturas.first().asignatura.id
print(f'\n=== CREANDO EVALUACIÓN ===')

try:
    evento_evaluacion = CalendarioClase.objects.create(
        nombre_actividad='Prueba de Comprensión Lectora - TEST',
        asignatura_id=asignatura_id,
        descripcion='Evaluación de comprensión lectora sobre textos narrativos',
        materiales='Lápiz, goma, concentración',
        fecha=date(2024, 12, 21),
        hora=time(9, 45)
    )
    print(f'✅ Evento creado: {evento_evaluacion.nombre_actividad}')
    print(f'   ID: {evento_evaluacion.id}')
    print(f'   Fecha: {evento_evaluacion.fecha} {evento_evaluacion.hora}')
    print(f'   Asignatura: {evento_evaluacion.asignatura.nombre}')
except Exception as e:
    print(f'❌ Error: {e}')

# Crear evento general del colegio
print(f'\n=== CREANDO EVENTO GENERAL ===')

try:
    evento_general = CalendarioColegio.objects.create(
        nombre_actividad='Junta de Profesores - TEST',
        descripcion='Reunión mensual de planificación académica',
        fecha=date(2024, 12, 19),
        hora=time(16, 0),
        encargado=f'{docente.usuario.nombre} {docente.usuario.apellido_paterno}',
        ubicacion='Sala de Profesores'
    )
    print(f'✅ Evento creado: {evento_general.nombre_actividad}')
    print(f'   ID: {evento_general.id}')
    print(f'   Fecha: {evento_general.fecha} {evento_general.hora}')
    print(f'   Encargado: {evento_general.encargado}')
except Exception as e:
    print(f'❌ Error: {e}')

# Verificar que aparezcan en la función de eventos
print(f'\n=== VERIFICANDO EN FUNCIÓN DE EVENTOS ===')
from Core.views.docentes import get_eventos_calendario_docente

eventos = get_eventos_calendario_docente(docente.pk)
print(f'Total eventos después de crear: {len(eventos)}')

# Buscar nuestros eventos TEST
eventos_test = [e for e in eventos if 'TEST' in e['title']]
print(f'Eventos TEST encontrados: {len(eventos_test)}')
for evento in eventos_test:
    print(f'- {evento["title"]} | {evento["start"]} | {evento["extendedProps"]["type"]}')

print(f'\n=== TEST COMPLETADO ===') 