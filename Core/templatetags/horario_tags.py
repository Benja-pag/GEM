from django import template
from Core.models import HorarioCurso

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter para acceder a elementos de un diccionario por clave
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def split(value, arg):
    """
    Template filter para dividir una cadena por un separador
    """
    if value is None:
        return []
    return value.split(arg)

@register.simple_tag
def get_hora_inicio_bloque(numero_bloque, dia):
    """
    Obtiene la hora de INICIO de un bloque y día específicos.
    Ej: '13:45'
    """
    try:
        horario = HorarioCurso.objects.filter(
            bloque=str(numero_bloque),
            dia=dia.upper(),
            actividad='CLASE'
        ).first()
        
        if horario:
            partes = horario.get_bloque_display().split(' - ')
            return partes[0]
        return f"B{numero_bloque}"
    except Exception:
        return f"B{numero_bloque}"

@register.simple_tag
def get_hora_fin_bloque(numero_bloque, dia):
    """
    Obtiene la hora de FIN de un bloque y día específicos.
    Ej: '14:30'
    """
    try:
        horario = HorarioCurso.objects.filter(
            bloque=str(numero_bloque),
            dia=dia.upper(),
            actividad='CLASE'
        ).first()
        
        if horario:
            partes = horario.get_bloque_display().split(' - ')
            if len(partes) > 1:
                return partes[1]
            return partes[0] # Si no hay rango, devuelve la única parte
        return f"B{numero_bloque}"
    except Exception:
        return f"B{numero_bloque}"

@register.filter
def dia_semana(fecha):
    """Convierte una fecha en el nombre del día de la semana en español"""
    dias = {
        'LUNES': 'Lunes',
        'MARTES': 'Martes',
        'MIERCOLES': 'Miércoles',
        'JUEVES': 'Jueves',
        'VIERNES': 'Viernes',
        'SABADO': 'Sábado',
        'DOMINGO': 'Domingo',
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    
    if isinstance(fecha, str):
        return dias.get(fecha.upper(), fecha)
    else:
        try:
            return dias[fecha.strftime('%A')]
        except:
            return str(fecha) 