from Core.models import AuthUser, Usuario, Docente, Estudiante, Administrativo
from django.contrib.auth.hashers import make_password
from django.db import transaction
from datetime import datetime


def obtener_usuario_por_rut(rut):
    """
    Obtiene un usuario por su RUT.
    :param rut: RUT del usuario a buscar.
    :return: Usuario encontrado o None si no existe.
    """
    try:
        return AuthUser.objects.get(rut=rut)
    except AuthUser.DoesNotExist:
        return None
def obtener_usuario_por_correo(correo):
    """
    Obtiene un usuario por su correo electrónico.
    :param correo: Correo del usuario a buscar.
    :return: Usuario encontrado o None si no existe.
    """
    try:
        return AuthUser.objects.get(correo=correo)
    except AuthUser.DoesNotExist:
        return None
def obtener_usuario_por_id(user_id):
    """
    Obtiene un usuario por su ID.
    :param user_id: ID del usuario a buscar.
    :return: Usuario encontrado o None si no existe.
    """
    try:
        auth_user = AuthUser.objects.get(id=user_id)
        return auth_user.usuario
    except AuthUser.DoesNotExist:
        return None
# Funcion principal para crear un usuario
def crear_usuario(data, tipo_usuario):
    try:
        with transaction.atomic():
            # Primero creamos el AuthUser (autenticación)
            auth_user = AuthUser.objects.create_user(
                rut=data['rut'],
                div=data['div'],
                password=data['password']
            )
            
            if tipo_usuario == 'ADMINISTRATIVO':
                auth_user.is_admin = True
                auth_user.save()

            # Luego creamos el Usuario (información personal)
            usuario = Usuario.objects.create(
                auth_user=auth_user,
                nombre=data['nombre'],
                apellido_paterno=data['apellido_paterno'],
                apellido_materno=data['apellido_materno'],
                rut=data['rut'],
                div=data['div'],
                correo=data['correo'],
                telefono=data.get('telefono', ''),
                direccion=data.get('direccion', ''),
                fecha_nacimiento=data.get('fecha_nacimiento')
            )

            # Finalmente, creamos el tipo específico de usuario
            if tipo_usuario == 'ESTUDIANTE':
                Estudiante.objects.create(
                    usuario=usuario,
                    contacto_emergencia=data.get('contacto_emergencia', ''),
                    curso_id=data.get('curso')
                )
            elif tipo_usuario == 'DOCENTE':
                Docente.objects.create(
                    usuario=usuario,
                    especialidad_id=data.get('especialidad'),
                    es_profesor_jefe=data.get('es_profesor_jefe', False)
                )
            elif tipo_usuario == 'ADMINISTRATIVO':
                Administrativo.objects.create(
                    usuario=usuario,
                    rol=data.get('rol_administrativo', 'ADMINISTRATIVO')
                )

            return usuario
    except Exception as e:
        raise Exception(f"Error al crear usuario: {str(e)}")
    
def actualizar_usuario(usuario, data):
    """
    Actualiza los datos de un usuario existente.
    :param usuario: Usuario a actualizar.
    :param data: Datos a actualizar.
    :return: Usuario actualizado.
    """
    with transaction.atomic():
        # Actualizar AuthUser
        auth_user = usuario.auth_user
        auth_user.rut = data.get('rut', auth_user.rut)
        auth_user.div = data.get('div', auth_user.div)
        if 'password' in data:
            auth_user.password = make_password(data['password'])
        auth_user.save()

        # Actualizar Usuario
        usuario.nombre = data.get('nombre', usuario.nombre)
        usuario.apellido_paterno = data.get('apellido_paterno', usuario.apellido_paterno)
        usuario.apellido_materno = data.get('apellido_materno', usuario.apellido_materno)
        usuario.correo = data.get('correo', usuario.correo)
        usuario.telefono = data.get('telefono', usuario.telefono)
        usuario.direccion = data.get('direccion', usuario.direccion)
        
        # Manejar fecha_nacimiento
        fecha_nacimiento = data.get('fecha_nacimiento')
        if fecha_nacimiento:
            if isinstance(fecha_nacimiento, str):
                try:
                    usuario.fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
                except ValueError:
                    # Si el formato no es correcto, mantener la fecha actual
                    pass
            else:
                usuario.fecha_nacimiento = fecha_nacimiento
        usuario.save()

        # Actualizar tipo de usuario específico
        if hasattr(usuario, 'estudiante'):
            estudiante = usuario.estudiante
            estudiante.contacto_emergencia = data.get('contacto_emergencia', estudiante.contacto_emergencia)
            estudiante.curso_id = data.get('curso', estudiante.curso_id)
            estudiante.save()
        elif hasattr(usuario, 'docente'):
            docente = usuario.docente
            docente.especialidad = data.get('especialidad', docente.especialidad)
            docente.save()
        elif hasattr(usuario, 'administrativo'):
            administrativo = usuario.administrativo
            administrativo.rol = data.get('rol_administrativo', administrativo.rol)
            administrativo.save()

    return usuario


# def cambiar_tipo_usuario(usuario, nuevo_tipo):
#     """
#     Cambia el tipo de usuario de un usuario existente.
#     :param usuario: Usuario a actualizar.
#     :param nuevo_tipo: Nuevo tipo de usuario.
#     :return: Usuario actualizado.
#     """
#     with transaction.atomic():
#         # Eliminar el tipo actual
#         if hasattr(usuario, 'estudiante'):
#             usuario.estudiante.delete()
#         elif hasattr(usuario, 'docente'):
#             usuario.docente.delete()
#         elif hasattr(usuario, 'administrativo'):
#             usuario.administrativo.delete()

#         # Crear el nuevo tipo
#         if nuevo_tipo == 'ESTUDIANTE':
#             Estudiante.objects.create(usuario=usuario)
#         elif nuevo_tipo == 'DOCENTE':
#             Docente.objects.create(usuario=usuario)
#         elif nuevo_tipo == 'ADMINISTRATIVO':
#             Administrativo.objects.create(usuario=usuario)

#     return usuario

def limpiar_authusers_huerfanos():
    """
    Elimina todos los registros de AuthUser que no tienen un Usuario asociado.
    """
    try:
        with transaction.atomic():
            # Encontrar todos los AuthUsers que no tienen un Usuario asociado
            auth_users_huerfanos = AuthUser.objects.filter(usuario__isnull=True)
            cantidad = auth_users_huerfanos.count()
            
            # Eliminar los registros huérfanos
            auth_users_huerfanos.delete()
            
            return cantidad
    except Exception as e:
        raise Exception(f"Error al limpiar AuthUsers huérfanos: {str(e)}")