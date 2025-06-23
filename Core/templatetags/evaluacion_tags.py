from django import template
from django.db.models import Avg

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Obtiene un elemento de un diccionario por clave
    """
    return dictionary.get(key, [])

@register.filter
def get_evaluaciones_asignatura(evaluaciones_estudiante, asignatura_nombre):
    """
    Obtiene las evaluaciones de una asignatura específica
    """
    return evaluaciones_estudiante.get(asignatura_nombre, [])

@register.filter
def calcular_promedio_asignatura(evaluaciones):
    """
    Calcula el promedio de las evaluaciones de una asignatura
    """
    if not evaluaciones:
        return 0.0
    
    suma = sum(eval['nota'] for eval in evaluaciones)
    return round(suma / len(evaluaciones), 1)

@register.filter
def contar_evaluaciones_aprobadas(evaluaciones):
    """
    Cuenta las evaluaciones aprobadas
    """
    return sum(1 for eval in evaluaciones if eval['estado'] == 'Aprobado')

@register.filter
def porcentaje_aprobacion(evaluaciones):
    """
    Calcula el porcentaje de aprobación
    """
    if not evaluaciones:
        return 0
    
    aprobadas = sum(1 for eval in evaluaciones if eval['estado'] == 'Aprobado')
    return round((aprobadas / len(evaluaciones)) * 100, 1)

@register.filter
def sum_dict_values(dict_list, key):
    """
    Suma los valores de una clave específica en una lista de diccionarios
    """
    return sum(d.get(key, 0) for d in dict_list)

@register.filter
def div(value, arg):
    """
    Divide value por arg
    """
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    """
    Multiplica value por arg
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sub(value, arg):
    """
    Resta arg de value
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0 