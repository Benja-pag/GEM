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
from Core.views.docentes import CancelarClaseView, MarcarClaseRecuperadaView, ObtenerHorariosAsignaturaView, CrearEventoCalendarioView, EditarEventoCalendarioView, EliminarEventoCalendarioView
from Core.views.admin import AdminEventosCalendarioView, AdminCrearEventoCalendarioView, AdminEditarEventoCalendarioView, AdminEliminarEventoCalendarioView, AdminDetalleEventoCalendarioView, ApiCursosView, ApiAsignaturasView
from Core.views.reportes import DashboardMetricasView, ReporteAsistenciaGeneralView, ReporteEvaluacionesView
from Core.views.reportes_simple import ReporteRendimientoCursosViewSimple, ReporteDocentesViewSimple, ReporteEstudiantesRiesgoViewSimple
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
    
    # URLs para cancelación de clases
    path('cancelar-clase/', CancelarClaseView.as_view(), name='cancelar_clase'),
    path('marcar-clase-recuperada/', MarcarClaseRecuperadaView.as_view(), name='marcar_clase_recuperada'),
    
    # URLs para horarios de asignaturas
    path('obtener-horarios-asignatura/<int:asignatura_id>/', ObtenerHorariosAsignaturaView.as_view(), name='obtener_horarios_asignatura'),
    
    # URLs para eventos del calendario (docentes)
    path('crear-evento-calendario/', CrearEventoCalendarioView.as_view(), name='crear_evento_calendario'),
    path('editar-evento-calendario/<int:evento_id>/', EditarEventoCalendarioView.as_view(), name='editar_evento_calendario'),
    path('eliminar-evento-calendario/<int:evento_id>/', EliminarEventoCalendarioView.as_view(), name='eliminar_evento_calendario'),
    
    # URLs para eventos del calendario (administrador)
    path('admin-eventos-calendario/', AdminEventosCalendarioView.as_view(), name='admin_eventos_calendario'),
    path('admin-crear-evento-calendario/', AdminCrearEventoCalendarioView.as_view(), name='admin_crear_evento_calendario'),
    path('admin-detalle-evento-calendario/<str:evento_id>/', AdminDetalleEventoCalendarioView.as_view(), name='admin_detalle_evento_calendario'),
    path('admin-editar-evento-calendario/<str:evento_id>/', AdminEditarEventoCalendarioView.as_view(), name='admin_editar_evento_calendario'),
    path('admin-eliminar-evento-calendario/<str:evento_id>/', AdminEliminarEventoCalendarioView.as_view(), name='admin_eliminar_evento_calendario'),
    
    # APIs para formularios
    path('api/cursos/', ApiCursosView.as_view(), name='api_cursos'),
    path('api/asignaturas/', ApiAsignaturasView.as_view(), name='api_asignaturas'),
    
    # URLs para reportes del admin
    path('api/dashboard-metricas/', DashboardMetricasView.as_view(), name='dashboard_metricas'),
    path('api/reporte-rendimiento-cursos/', ReporteRendimientoCursosViewSimple.as_view(), name='reporte_rendimiento_cursos'),
    path('api/reporte-asistencia-general/', ReporteAsistenciaGeneralView.as_view(), name='reporte_asistencia_general'),
    path('api/reporte-docentes/', ReporteDocentesViewSimple.as_view(), name='reporte_docentes'),
    path('api/reporte-estudiantes-riesgo/', ReporteEstudiantesRiesgoViewSimple.as_view(), name='reporte_estudiantes_riesgo'),
    path('api/reporte-evaluaciones/', ReporteEvaluacionesView.as_view(), name='reporte_evaluaciones'),
]

