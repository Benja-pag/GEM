from Core.servicios.helpers.constantes import TIPOS_USUARIO
from Core.servicios.repos.usuarios import obtener_usuario_por_rut, obtener_usuario_por_correo
import re
from datetime import datetime, date

def es_cadena_valida(valor):
    return isinstance(valor, str) and bool(valor.strip())

def es_correo_valido(mail):
    return isinstance(mail, str) and '@' in mail and '.' in mail

def es_correo_existente(mail):
    return obtener_usuario_por_correo(mail) is not None

def validar_data_crear_usuario(data, tipo_usuario='ESTUDIANTE'):
    errores = []

    # Validar campos básicos obligatorios
    campos_obligatorios = [
        'nombre', 'apellido_paterno', 'apellido_materno',
        'rut', 'div', 'correo', 'telefono', 'direccion',
        'fecha_nacimiento', 'password'
    ]
    
    for campo in campos_obligatorios:
        if campo not in data or not data[campo]:
            errores.append(f"El campo {campo.replace('_', ' ')} es obligatorio.")
    
    # Si hay errores en campos obligatorios, retornar
    if errores:
        return False, errores

    # Validar RUT
    if not validar_formato_rut(data['rut']):
        errores.append("El formato del RUT no es válido.")
    
    # Validar correo electrónico institucional
    if not data['correo'].endswith('@gem.cl'):
        errores.append("El correo electrónico debe ser institucional (@gem.cl).")
    
    # Validar teléfono (9 dígitos)
    if not re.match(r'^\d{9}$', data['telefono']):
        errores.append("El teléfono debe tener 9 dígitos numéricos.")
    
    # Validar contraseña    
    if len(data['password']) < 8:
        errores.append("La contraseña debe tener al menos 8 caracteres.")
    
    # Validar que las contraseñas coincidan
    if 'confirm_password' in data and data['password'] != data['confirm_password']:
        errores.append("Las contraseñas no coinciden.")
    
    # Validar fecha de nacimiento
    try:
        fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        
        if tipo_usuario == 'ESTUDIANTE':
            if edad < 10 or edad > 20:
                errores.append("La edad del estudiante debe estar entre 10 y 20 años.")
        elif tipo_usuario in ['DOCENTE', 'ADMINISTRATIVO']:
            if edad < 21:
                errores.append("Debe ser mayor de 21 años.")
    except ValueError:
        errores.append("La fecha de nacimiento no tiene un formato válido.")
    
    # Validar campos específicos según el tipo de usuario
    if tipo_usuario == 'ESTUDIANTE':
        if 'contacto_emergencia' not in data or not data['contacto_emergencia']:
            errores.append("El contacto de emergencia es obligatorio para estudiantes.")
        if 'curso' not in data or not data['curso']:
            errores.append("El curso es obligatorio para estudiantes.")
            
    elif tipo_usuario == 'DOCENTE':
        if 'especialidad' not in data or not data['especialidad']:
            errores.append("La especialidad es obligatoria para docentes.")
        if 'es_profesor_jefe' not in data:
            data['es_profesor_jefe'] = False
            
    elif tipo_usuario == 'ADMINISTRATIVO':
        if 'rol' not in data or not data['rol']:
            errores.append("El rol administrativo es obligatorio.")
        elif data['rol'] not in ['ADMINISTRADOR', 'ADMINISTRATIVO']:
            errores.append("El rol administrativo seleccionado no es válido.")
   
    return len(errores) == 0, errores

def validar_formato_rut(rut):
    return bool(re.match(r'^[0-9]{7,8}$', rut))

def validar_formato_correo(correo):
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@gem\.cl$', correo))

def validar_formato_telefono(telefono):
    return bool(re.match(r'^[0-9]{9}$', telefono))