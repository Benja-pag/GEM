from .usuarios import *
from .cursos import *
from .notas import *
from .chat import *
from .calendarios import *
from .academico import *
from .administrativo import *
from .colegio import *

__all__ = [
    # Modelos de Usuarios
    'AuthUser', 'Usuario', 'Administrativo', 'Docente', 'Estudiante', 'ProfesorJefe', 'Especialidad',
    
    # Modelos de Cursos
    'Asignatura', 'AsignaturaImpartida', 'AsignaturaInscrita', 'Clase', 'Curso', 'Asistencia', 'HorarioCurso',
    
    # Modelos de Notas
    'EvaluacionBase', 'Evaluacion', 'AlumnoEvaluacion',
    
    # Modelos de Chat
    'Foro', 'MensajeForo', 'ChatClase', 'ChatGrupo',
    
    # Modelos de Calendarios
    'CalendarioClase', 'CalendarioColegio',
    
    # Nuevos Modelos Académicos
    'MaterialClase', 'Tarea', 'AnotacionCurso', 'ObjetivoAsignatura', 'RecursoAsignatura',
    
    # Nuevos Modelos Administrativos
    'ConfiguracionColegio', 'LogActividad',
    
    # Modelo de Colegio
    'Colegio'
]
