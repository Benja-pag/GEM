import os
import django
import sys
from datetime import date, time, timedelta
import random
import calendar

# Agrega el directorio raíz del proyecto al path (sube dos niveles desde subcarpeta)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configura el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import CalendarioColegio, CalendarioClase, Asignatura

def poblar_eventos_calendario(num_eventos_colegio=2, num_eventos_clase=4):
    """
    Puebla la base de datos con eventos de calendario de prueba para el mes actual y el siguiente.
    
    Args:
        num_eventos_colegio (int): Número de eventos de colegio a crear por mes.
        num_eventos_clase (int): Número de eventos de clase (evaluaciones) a crear por mes.
    """
    print('--- 📅 Iniciando generación de eventos de prueba para el calendario ---')

    # 1. Limpiar eventos de prueba anteriores
    try:
        num_colegio_deleted, _ = CalendarioColegio.objects.filter(descripcion__icontains='Evento generado automáticamente').delete()
        num_clase_deleted, _ = CalendarioClase.objects.filter(descripcion__icontains='Evento generado automáticamente').delete()
        print(f'🧹 Eliminados {num_colegio_deleted} eventos de colegio y {num_clase_deleted} eventos de clase de pruebas anteriores.')
    except Exception as e:
        print(f"Error al limpiar eventos anteriores: {e}")
        return

    # Helper para obtener un día aleatorio en un mes específico
    def random_day_in_month(year, month):
        _, num_days = calendar.monthrange(year, month)
        return date(year, month, random.randint(1, num_days))

    today = date.today()
    asignaturas = list(Asignatura.objects.all())

    if not asignaturas:
        print('⚠️ Advertencia: No se encontraron asignaturas. No se pueden crear eventos de clase.')
        return

    # 2. Generar eventos para el mes actual
    current_year, current_month = today.year, today.month
    print(f'\n🗓️  Generando eventos para el mes actual ({current_month}/{current_year})...')
    
    # Eventos de colegio
    for i in range(num_eventos_colegio):
        CalendarioColegio.objects.create(
            nombre_actividad=f'Actividad Colegio {i+1}',
            descripcion='Evento generado automáticamente por script de población.',
            fecha=random_day_in_month(current_year, current_month),
            hora=time(random.randint(10, 15), 0),
            encargado='Dirección',
            ubicacion='Campus Central'
        )
    
    # Eventos de clase (evaluaciones)
    for i in range(num_eventos_clase):
        CalendarioClase.objects.create(
            nombre_actividad=f'Evaluación {i+1}',
            descripcion='Evento generado automáticamente por script de población.',
            asignatura=random.choice(asignaturas),
            fecha=random_day_in_month(current_year, current_month),
            hora=time(random.randint(9, 14), 30)
        )
    print(f'✅ {num_eventos_colegio} eventos de colegio y {num_eventos_clase} de clase creados para el mes actual.')

    # 3. Generar eventos para el próximo mes
    next_month_date = (today.replace(day=28) + timedelta(days=5)) # Manera segura de llegar al siguiente mes
    next_year, next_month = next_month_date.year, next_month_date.month
    print(f'\n🗓️  Generando eventos para el próximo mes ({next_month}/{next_year})...')

    # Eventos de colegio
    for i in range(num_eventos_colegio):
        CalendarioColegio.objects.create(
            nombre_actividad=f'Actividad Colegio (Próx. Mes) {i+1}',
            descripcion='Evento generado automáticamente por script de población.',
            fecha=random_day_in_month(next_year, next_month),
            hora=time(random.randint(10, 15), 0),
            encargado='Dirección',
            ubicacion='Campus Central'
        )
    
    # Eventos de clase (evaluaciones)
    for i in range(num_eventos_clase):
        CalendarioClase.objects.create(
            nombre_actividad=f'Evaluación (Próx. Mes) {i+1}',
            descripcion='Evento generado automáticamente por script de población.',
            asignatura=random.choice(asignaturas),
            fecha=random_day_in_month(next_year, next_month),
            hora=time(random.randint(9, 14), 30)
        )
    print(f'✅ {num_eventos_colegio} eventos de colegio y {num_eventos_clase} de clase creados para el próximo mes.')
    print('\n🎉 ¡Población de eventos de calendario completada exitosamente!')

if __name__ == '__main__':
    poblar_eventos_calendario() 