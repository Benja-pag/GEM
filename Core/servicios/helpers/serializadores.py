def usuario_a_dict(user):
    return {
        'id': user.id,
        'nombre': user.nombre,
        'apellido_paterno': user.apellido_paterno,
        'apellido_materno': user.apellido_materno,
        'rut': user.rut,
        'div': user.div,
        'correo': user.correo,
        'telefono': user.telefono,
        'direccion': user.direccion,
        'fecha_nacimiento': user.fecha_nacimiento,
    }