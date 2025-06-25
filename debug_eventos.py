import os
import django
import sys
import json
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Docente, AsignaturaImpartida, CalendarioClase, CalendarioColegio
from Core.views.docentes import get_eventos_calendario_docente

# Encontrar Juan Pérez
docente = Docente.objects.get(usuario__nombre='Juan', usuario__apellido_paterno='Perez')
print(f'Juan Pérez ID: {docente.pk}')

# Ver sus asignaturas
asignaturas = AsignaturaImpartida.objects.filter(docente=docente)
print(f'\nAsignaturas que imparte Juan: {asignaturas.count()}')
for a in asignaturas:
    print(f'- {a.asignatura.nombre} (asignatura_id: {a.asignatura_id})')

# Verificar eventos
print(f'\n=== DIAGNOSTICO DE EVENTOS ===')
eventos = get_eventos_calendario_docente(docente.pk)  # Ahora devuelve lista directamente
print(f'Total eventos para Juan: {len(eventos)}')

print(f'\n=== EVENTOS QUE DEBERIAN MOSTRARSE ===')
for i, evento in enumerate(eventos, 1):
    print(f'{i}. {evento["title"]} | {evento["start"]} | Tipo: {evento["extendedProps"]["type"]}')

# Verificar eventos específicos que creé
print(f'\n=== MIS EVENTOS CREADOS ===')
mi_evento_clase = CalendarioClase.objects.filter(nombre_actividad__contains='Juan Pérez').first()
if mi_evento_clase:
    print(f'CalendarioClase: {mi_evento_clase.nombre_actividad} - {mi_evento_clase.fecha} {mi_evento_clase.hora}')

mi_evento_colegio = CalendarioColegio.objects.filter(encargado__contains='Juan').first()
if mi_evento_colegio:
    print(f'CalendarioColegio: {mi_evento_colegio.nombre_actividad} - {mi_evento_colegio.fecha} {mi_evento_colegio.hora}')

# Verificar fechas para ver si están en el futuro
from datetime import date
hoy = date.today()
print(f'\n=== ANALISIS DE FECHAS (hoy: {hoy}) ===')
for evento in eventos:
    fecha_evento = evento["start"].split('T')[0]
    print(f'- {evento["title"]}: {fecha_evento}')

# Test del JSON conversion
import json
eventos_json = json.dumps(eventos)
print(f'\n=== JSON STRING PARA TEMPLATE ===')
print(f'JSON length: {len(eventos_json)}')
print(f'JSON preview: {eventos_json[:200]}...')

# Test parsing
eventos_parsed = json.loads(eventos_json)
print(f'Eventos parsed: {len(eventos_parsed)}') 