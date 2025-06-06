from .usuarios import *
from .admin import *
from .alumnos import *
from .auth import *
from .asignaturas import *
from .docentes import *
from .evaluaciones import *
from .template_vistas import *
from .calendario import *
from .template_vistas import HomeView, SurveysView, TasksView, TestsView
from .admin import AdminPanelView, ToggleUserStatusView, CreateAdminView
from .usuarios import UserManagementView, UserCreateView, UserDetailView, UserUpdateView, UserDeleteView
from .docentes import ProfesorPanelView
from .alumnos import EstudiantePanelView, AttendanceView
from .auth import LoginView, LogoutView, RegisterView, ChangePasswordView
from .calendario import CalendarioView, CalendarioEventosView, CalendarioGuardarEventoView, CalendarioEliminarEventoView
from .cursos import CursoDetalleView, AsignaturaDetalleView

__all__ = [
    'HomeView',
    'AdminPanelView',
    'UserManagementView',
    'UserCreateView',
    'UserDetailView',
    'UserUpdateView',
    'UserDeleteView',
    'ToggleUserStatusView',
    'CreateAdminView',
    'ProfesorPanelView',
    'EstudiantePanelView',
    'LoginView',
    'LogoutView',
    'RegisterView',
    'ChangePasswordView',
    'SurveysView',
    'TasksView',
    'TestsView',
    'CalendarioView',
    'CalendarioEventosView',
    'CalendarioGuardarEventoView',
    'CalendarioEliminarEventoView',
    'AttendanceView',
    'CursoDetalleView',
    'AsignaturaDetalleView'
]
