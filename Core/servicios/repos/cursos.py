from Core.models import AuthUser, Usuario, Docente, Estudiante, Administrativo
from django.contrib.auth.hashers import make_password
from django.db import transaction

def get_estudiantes_por_curso(id_curso):
    """
    Obtiene los estudiantes de un curso específico.
    :param id_curso: ID del curso.
    :return: Lista de estudiantes en el curso.
    """
    return Estudiante.objects.filter(curso=id_curso).select_related('usuario')
def get_curso(id_curso):
    """
    Obtiene un curso por su ID.
    :param id_curso: ID del curso.
    :return: Objeto Curso.
    """
    return Curso.objects.get(id=id_curso)