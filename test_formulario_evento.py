import os
import django
import sys
import json
from datetime import date, time
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from Core.models import Docente, AsignaturaImpartida, CalendarioClase, CalendarioColegio, Usuario, AuthUser
from Core.views.docentes import CrearEventoCalendarioView

print("=== SIMULANDO FORMULARIO DE EVENTO ===")

# Obtener Juan Pérez
docente = Docente.objects.get(usuario__nombre='Juan', usuario__apellido_paterno='Perez')
asignatura_impartida = AsignaturaImpartida.objects.filter(docente=docente).first()
print(f'Juan Pérez ID: {docente.pk}')
print(f'AsignaturaImpartida ID: {asignatura_impartida.id}')

# Crear request simulado
factory = RequestFactory()

# Datos que enviaría el formulario
form_data = {
    'tipo': 'EVALUACION',
    'titulo': 'Simulación de Evaluación - FORM TEST',
    'descripcion': 'Esta es una evaluación creada desde el formulario simulado',
    'fecha': '2024-12-22',
    'bloque_horario': '3-4',
    'asignatura_id': str(asignatura_impartida.id),  # AsignaturaImpartida ID: 104
    'ubicacion': 'SALA-4B',
    'materiales': 'Lápiz y goma',
    'instrucciones': 'Responder todas las preguntas',
    'ponderacion': '30',
    'tipo_evaluacion': 'PRUEBA'
}

print(f"\n=== DATOS DEL FORMULARIO ===")
for key, value in form_data.items():
    print(f"{key}: {value}")

# Crear request POST
request = factory.post('/crear-evento-calendario/', form_data)

# Simular autenticación
auth_user = AuthUser.objects.get(id=docente.usuario.auth_user_id)
request.user = auth_user

# Crear vista y procesar
view = CrearEventoCalendarioView()
view.request = request

print(f"\n=== PROCESANDO VISTA ===")
try:
    response = view.post(request)
    response_data = json.loads(response.content.decode())
    print(f"Respuesta: {response_data}")
    
    if response_data.get('success'):
        print(f"✅ Evento creado exitosamente: {response_data.get('message')}")
    else:
        print(f"❌ Error: {response_data.get('error')}")
        
except Exception as e:
    print(f"❌ Excepción: {e}")

print(f"\n=== VERIFICANDO EN BD ===")
# Verificar si se creó
evento_test = CalendarioClase.objects.filter(nombre_actividad__contains='FORM TEST').first()
if evento_test:
    print(f"✅ Evento encontrado en BD: {evento_test.nombre_actividad}")
else:
    print("❌ Evento no encontrado en BD")

print(f"\n=== TEST COMPLETADO ===") 