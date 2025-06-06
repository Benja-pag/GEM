from django.urls import path
from Core.views import (
    HomeView, AdminPanelView, UserManagementView, UserCreateView, CalendarioView,
    UserDetailView, UserUpdateView, UserDeleteView, ProfesorPanelView,
    EstudiantePanelView, AttendanceView, LoginView, LogoutView,
    RegisterView, CreateAdminView, ChangePasswordView,
    UserDataView, SurveysView, TasksView, TestsView, ToggleUserStatusView,
    CalendarioEventosView, CalendarioGuardarEventoView, CalendarioEliminarEventoView,
    CursoDetalleView, AsignaturaDetalleView, CleanupAuthUsersView
)

urlpatterns = [
    # URLs de autenticación
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # URLs principales
    path('', HomeView.as_view(), name='home'),
    path('admin-panel/', AdminPanelView.as_view(), name='admin_panel'),
    path('users/', UserManagementView.as_view(), name='users'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:user_id>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:user_id>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:user_id>/toggle-status/', ToggleUserStatusView.as_view(), name='toggle_user_status'),
    path('users/<int:user_id>/data/', UserDataView.as_view(), name='user_data'),
    path('users/cleanup-auth/', CleanupAuthUsersView.as_view(), name='cleanup_auth_users'),
    
    path('profesor-panel/', ProfesorPanelView.as_view(), name='profesor_panel'),
    path('estudiante-panel/', EstudiantePanelView.as_view(), name='estudiante_panel'),
    path('attendance/', AttendanceView.as_view(), name='attendance'),
    path('create-admin/', CreateAdminView.as_view(), name='create_admin'),
    
    path('surveys/', SurveysView.as_view(), name='surveys'),
    path('tasks/', TasksView.as_view(), name='tasks'),
    path('tests/', TestsView.as_view(), name='tests'),
    path('core/stats/', AdminPanelView.as_view(), name='core_stats'),

    # URLs del Calendario
    path('calendar/', CalendarioView.as_view(), name='calendar'),
    path('calendar/events/', CalendarioEventosView.as_view(), name='calendar_events'),
    path('calendar/save-event/', CalendarioGuardarEventoView.as_view(), name='calendar_save_event'),
    path('calendar/delete-event/', CalendarioEliminarEventoView.as_view(), name='calendar_delete_event'),

    # URLs de cursos y asignaturas
    path('curso/<int:curso_id>/', CursoDetalleView.as_view(), name='curso_detalle'),
    path('asignatura/<int:asignatura_id>/', AsignaturaDetalleView.as_view(), name='asignatura_detalle'),
]

