def usuario_a_dict(user):
    """
    Convierte un objeto Usuario en un diccionario con toda su información,
    incluyendo datos específicos según el tipo de usuario.
    """
    data = {
        'id': user.auth_user.id,
        'nombre': user.nombre,
        'apellido_paterno': user.apellido_paterno,
        'apellido_materno': user.apellido_materno,
        'nombre_completo': f'{user.nombre} {user.apellido_paterno} {user.apellido_materno}',
        'rut': user.rut,
        'div': user.div,
        'rut_completo': f'{user.rut}-{user.div}',
        'correo': user.correo,
        'telefono': user.telefono,
        'direccion': user.direccion,
        'fecha_nacimiento': user.fecha_nacimiento.strftime('%Y-%m-%d') if user.fecha_nacimiento else None,
        'fecha_creacion': user.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if user.fecha_creacion else None,
        'activador': user.activador,
        'tipo_usuario': 'estudiante' if hasattr(user, 'estudiante') else 'docente' if hasattr(user, 'docente') else 'administrativo'
    }

    # Agregar información específica según el tipo de usuario
    if hasattr(user, 'estudiante'):
        data.update({
            'contacto_emergencia': user.estudiante.contacto_emergencia,
            'curso': {
                'id': user.estudiante.curso.id if user.estudiante.curso else None,
                'nombre': str(user.estudiante.curso) if user.estudiante.curso else None
            } if hasattr(user.estudiante, 'curso') else None
        })
    elif hasattr(user, 'docente'):
        data.update({
            'especialidad': {
                'id': user.docente.especialidad.id if user.docente.especialidad else None,
                'nombre': str(user.docente.especialidad) if user.docente.especialidad else None
            } if hasattr(user.docente, 'especialidad') else None,
            'es_profesor_jefe': user.docente.es_profesor_jefe
        })
    elif hasattr(user, 'administrativo'):
        data.update({
            'rol_administrativo': user.administrativo.rol
        })

    return data