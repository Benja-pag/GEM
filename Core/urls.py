from django.urls import path, include
from Core.views import (
    HomeView, AdminPanelView, AdminPanelModularView, UserManagementView, UserCreateView,
    UserDetailView, UserUpdateView, UserDeleteView, ProfesorPanelView, ProfesorPanelModularView,
    EstudiantePanelView, EstudiantePanelModularView, AttendanceView, LoginView, LogoutView,
    RegisterView, CreateAdminView, ChangePasswordView,
    UserDataView, SurveysView, TasksView, TestsView, ToggleUserStatusView,
    CursoDetalleView, AsignaturaDetalleView, AsignaturaDetalleEstudianteView, CleanupAuthUsersView
)
from Core.views.alumnos import InscribirElectivoView, InscribirElectivosLoteView, BorrarInscripcionElectivosView
from Core.views import foro as foro_views
from Core.views import pdf_views as pdf_views

urlpatterns = [
    # URLs de autenticación
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # URLs principales (paneles modulares)
    path('', HomeView.as_view(), name='home'),
    path('admin-panel/', AdminPanelModularView.as_view(), name='admin_panel'),
    path('profesor-panel/', ProfesorPanelModularView.as_view(), name='profesor_panel'),
    path('estudiante-panel/', EstudiantePanelModularView.as_view(), name='estudiante_panel'),
    
    # URLs alternativas para paneles antiguos
    path('admin-panel-antiguo/', AdminPanelView.as_view(), name='admin_panel_antiguo'),
    path('profesor-panel-antiguo/', ProfesorPanelView.as_view(), name='profesor_panel_antiguo'),
    path('estudiante-panel-antiguo/', EstudiantePanelView.as_view(), name='estudiante_panel_antiguo'),
    
    # URLs de gestión de usuarios
    path('users/', UserManagementView.as_view(), name='users'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:user_id>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:user_id>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:user_id>/toggle-status/', ToggleUserStatusView.as_view(), name='toggle_user_status'),
    path('users/<int:user_id>/data/', UserDataView.as_view(), name='user_data'),
    path('users/cleanup-auth/', CleanupAuthUsersView.as_view(), name='cleanup_auth_users'),
    
    path('attendance/', AttendanceView.as_view(), name='attendance'),
    path('create-admin/', CreateAdminView.as_view(), name='create_admin'),
    
    path('surveys/', SurveysView.as_view(), name='surveys'),
    path('tasks/', TasksView.as_view(), name='tasks'),
    path('tests/', TestsView.as_view(), name='tests'),
    path('core/stats/', AdminPanelModularView.as_view(), name='core_stats'),

    # URLs de cursos y asignaturas
    path('curso/<int:curso_id>/', CursoDetalleView.as_view(), name='curso_detalle'),
    path('asignatura/<int:asignatura_id>/', AsignaturaDetalleView.as_view(), name='asignatura_detalle'),
    path('asignatura-estudiante/<int:asignatura_id>/', AsignaturaDetalleEstudianteView.as_view(), name='asignatura_detalle_estudiante'),

    # URLs para el Foro
    path('foro/', include('Core.urls_foro')),

    # URLs para Comunicaciones
    path('comunicaciones/', include('Core.urls_comunicaciones')),
    
    # URLs para descarga de PDFs
    path('pdf/horario/', pdf_views.DescargarHorarioPDFView.as_view(), name='descargar_horario_pdf'),
    path('pdf/asistencia/', pdf_views.DescargarAsistenciaPDFView.as_view(), name='descargar_asistencia_pdf'),
    path('pdf/calificaciones/', pdf_views.DescargarCalificacionesPDFView.as_view(), name='descargar_calificaciones_pdf'),
]

urlpatterns += [
    path('inscribir-electivo/', InscribirElectivoView.as_view(), name='inscribir_electivo'),
    path('inscribir-electivos-lote/', InscribirElectivosLoteView.as_view(), name='inscribir_electivos_lote'),
    path('borrar-inscripcion-electivos/', BorrarInscripcionElectivosView.as_view(), name='borrar_inscripcion_electivos'),
]

