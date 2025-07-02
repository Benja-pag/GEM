from django.contrib import messages

def agregar_mensaje_sistema(request, tipo, mensaje):
    """
    Agrega un mensaje del sistema que será mostrado al usuario usando el sistema GEM.
    
    Args:
        request: HttpRequest object
        tipo: str - 'success', 'error', 'info', 'warning'
        mensaje: str - El mensaje a mostrar
    """
    if request and hasattr(request, 'session'):
        # Agregar el mensaje a la sesión de Django
        messages.add_message(request, getattr(messages, tipo.upper()), mensaje)

# Funciones de conveniencia
def exito(request, mensaje):
    """Muestra un mensaje de éxito usando el estilo GEM."""
    agregar_mensaje_sistema(request, 'success', mensaje)

def error(request, mensaje):
    """Muestra un mensaje de error usando el estilo GEM."""
    agregar_mensaje_sistema(request, 'error', mensaje)

def info(request, mensaje):
    """Muestra un mensaje informativo usando el estilo GEM."""
    agregar_mensaje_sistema(request, 'info', mensaje)

def advertencia(request, mensaje):
    """Muestra un mensaje de advertencia usando el estilo GEM."""
    agregar_mensaje_sistema(request, 'warning', mensaje) 