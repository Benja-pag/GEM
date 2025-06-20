from django import template

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