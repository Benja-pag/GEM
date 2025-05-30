from Core.models import AsignaturaInscrita


def get_asignaturas_estudiante(estudiante_id):
    """
    Obtiene las asignaturas impartidas a un estudiante específico.
    :param estudiante_id: ID del estudiante.
    :return: Lista de asignaturas impartidas al estudiante.
    """
    return AsignaturaInscrita.objects.filter(estudiante=estudiante_id)