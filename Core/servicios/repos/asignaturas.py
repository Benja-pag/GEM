from Core.models import AsignaturaInscrita


def get_asignaturas_estudiante(estudiante_id):
    """
    Obtiene las asignaturas impartidas a un estudiante específico.
    :param estudiante_id: ID del estudiante.
    :return: Lista de asignaturas impartidas al estudiante con información del profesor.
    """
    return AsignaturaInscrita.objects.filter(
        estudiante=estudiante_id,
        validada=True  # Solo asignaturas validadas
    ).select_related(
        'asignatura_impartida__asignatura',
        'asignatura_impartida__docente__usuario'
    ).distinct(
        'asignatura_impartida__asignatura__nombre'
    ).order_by(
        'asignatura_impartida__asignatura__nombre'
    )