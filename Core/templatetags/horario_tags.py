from django import template
from Core.models import HorarioCurso
from itertools import groupby
from operator import attrgetter

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

@register.filter
def regroup_by(queryset, attrs):
    """
    Agrupa un queryset por múltiples atributos y elimina duplicados.
    Los atributos deben ser proporcionados como una cadena separada por comas.
    """
    if not queryset:
        return []

    # Convertir la cadena de atributos en una lista
    attrs = [attr.strip() for attr in attrs.split(',')]
    
    # Función para obtener los valores de los atributos
    def get_attrs(obj):
        values = []
        for attr in attrs:
            value = obj
            for part in attr.split('.'):
                value = getattr(value, part, None)
            values.append(value)
        return tuple(values)

    # Ordenar y agrupar por los atributos
    sorted_qs = sorted(queryset, key=get_attrs)
    grouped = groupby(sorted_qs, key=get_attrs)
    
    # Tomar solo el primer elemento de cada grupo
    return [next(g) for k, g in grouped]

@register.filter
def unique_by(queryset, attr):
    """
    Elimina duplicados de un queryset basado en un atributo.
    """
    if not queryset:
        return []

    # Función para obtener el valor del atributo
    def get_attr(obj):
        value = obj
        for part in attr.split('.'):
            value = getattr(value, part, None)
        return value

    # Ordenar y agrupar por el atributo
    sorted_qs = sorted(queryset, key=get_attr)
    grouped = groupby(sorted_qs, key=get_attr)
    
    # Tomar solo el primer elemento de cada grupo
    return [next(g) for k, g in grouped] 