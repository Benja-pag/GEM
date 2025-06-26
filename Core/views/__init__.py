from .usuarios import *
from .admin import *
from .alumnos import *
from .auth import *
from .docentes import *
from .template_vistas import *
from .template_vistas import HomeView, SurveysView, TasksView, TestsView
from .admin import AdminPanelView, AdminPanelModularView, ToggleUserStatusView, CreateAdminView
from .usuarios import UserManagementView, UserCreateView, UserDetailView, UserUpdateView, UserDeleteView
from .docentes import ProfesorPanelView
from .alumnos import EstudiantePanelView, AttendanceView
from .auth import LoginView, LogoutView, RegisterView, ChangePasswordView
from .cursos import CursoDetalleView, AsignaturaDetalleView, AsignaturaDetalleEstudianteView

__all__ = [
    'HomeView',
    'AdminPanelView',
    'AdminPanelModularView',
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
    'AttendanceView',
    'CursoDetalleView',
    'AsignaturaDetalleView',
    'AsignaturaDetalleEstudianteView'
]
