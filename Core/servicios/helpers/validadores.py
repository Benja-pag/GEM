from Core.servicios.helpers.constantes import TIPOS_USUARIO
from Core.servicios.repos.usuarios import obtener_usuario_por_rut, obtener_usuario_por_correo

def es_cadena_valida(valor):
    return isinstance(valor, str) and bool(valor.strip())

def es_correo_valido(mail):
    return isinstance(mail, str) and '@' in mail and '.' in mail

def es_correo_existente(mail):
    return obtener_usuario_por_correo(mail) is not None

def validar_data_crear_usuario(data):
    """
    Valida los datos para crear un nuevo usuario.
    :param data: Diccionario con los datos del usuario.
    :return: Tupla (es_valido, lista_de_errores)
    """  
    errores = []

    # Validar campos obligatorios
    campos = [
        ('rut', "El RUT es obligatorio."),
        ('div', "La división es obligatoria."),
        ('nombre', "El nombre es obligatorio."),
        ('apellido_paterno', "El apellido paterno es obligatorio."),
        ('apellido_materno', "El apellido materno es obligatorio."),
        ('correo', "El correo electrónico es obligatorio."),
        ('password', "La contraseña es obligatoria."),
        ('confirm_password', "La contraseña de confirmación es obligatoria."),
        ('telefono', "El teléfono es obligatorio."),
        ('direccion', "La dirección es obligatoria."),
        ('fecha_nacimiento', "La fecha de nacimiento es obligatoria."),
        ('tipo_usuario', "El tipo de usuario es obligatorio."),
    ]
    for campo, mensaje in campos:
        if campo not in data or not es_cadena_valida(data[campo]):
            errores.append(mensaje)
    if errores.__len__() > 0:
        return False, errores

    # Validar RUT
    if 'rut' in data and not es_cadena_valida(data['rut']):
        errores.append("El RUT no es válido.")
        return False, errores
    elif obtener_usuario_por_rut(data['rut']):
        errores.append("El RUT ya está en uso.")
        return False, errores
    
    # Validar correo
    if 'correo' in data and not es_correo_existente(data['correo']):
        errores.append("El correo electrónico no es válido.")
        return False, errores
    elif es_correo_existente(data['correo']):
        errores.append("El correo electrónico ya está en uso.")
        return False, errores
    
    # Validar contraseña    
    if 'password' in data and 'confirm_password' in data and data['password'] != data['confirm_password']:
        errores.append("Las contraseñas no coinciden.")
        return False, errores
    
    # Validar tipo de usuario
    tipos_validos = [t[0] for t in TIPOS_USUARIO]
    if 'tipo_usuario' not in data or data['tipo_usuario'] not in tipos_validos:
        errores.append(f"El tipo de usuario es obligatorio y debe ser uno de los siguientes: {', '.join(tipos_validos)}.")
        return False, errores
    
    # Validar campos específicos según el tipo de usuario
    if data['tipo_usuario'] == 'ESTUDIANTE':
        if 'contacto_emergencia' not in data or not es_cadena_valida(data['contacto_emergencia']):
            errores.append("El contacto de emergencia es obligatorio para estudiantes.")
    # elif data['tipo_usuario'] == 'DOCENTE':
    #     if 'especialidad' not in data or not es_cadena_valida(data['especialidad']):
    #         errores.append("La especialidad es obligatoria para docentes.")
   
    return len(errores) == 0, errores