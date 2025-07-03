from django.urls import path, include
from Core.views import (
    HomeView, AdminPanelView, AdminPanelModularView, UserManagementView, UserCreateView,
    UserDetailView, UserUpdateView, UserDeleteView, ProfesorPanelView, ProfesorPanelModularView,
    EstudiantePanelView, EstudiantePanelModularView, AttendanceView, LoginView, LogoutView,
    RegisterView, CreateAdminView, ChangePasswordView,
    UserDataView, SurveysView, TasksView, TestsView, ToggleUserStatusView,
    CursoDetalleView, AsignaturaDetalleView, AsignaturaDetalleEstudianteView, CleanupAuthUsersView,
    EstudianteDetalleView
)
from Core.views.alumnos import InscribirElectivoView, InscribirElectivosLoteView, BorrarInscripcionElectivosView
from Core.views.docentes import CancelarClaseView, MarcarClaseRecuperadaView, ObtenerHorariosAsignaturaView, ResumenGeneralDocenteView, ReporteEvaluacionesAsignaturasDocenteView, ReporteEvaluacionesCursoJefeView, ReporteAsistenciaAsignaturasDocenteView, ReporteAsistenciaCursoJefeView
from Core.views.admin import AdminEventosCalendarioView, AdminCrearEventoCalendarioView, AdminEditarEventoCalendarioView, AdminEliminarEventoCalendarioView, AdminDetalleEventoCalendarioView, ApiCursosView, ApiAsignaturasView, CursoDataView, CursoUpdateView, CursoDeleteView, AsignaturaDataView, AsignaturaUpdateView, AsignaturaDeleteView
from Core.views.reportes import DashboardMetricasView, ReporteAsistenciaGeneralView, ReporteEvaluacionesView
from Core.views.reportes_simple import ReporteRendimientoCursosViewSimple, ReporteDocentesViewSimple, ReporteEstudiantesRiesgoViewSimple, ReporteAsistenciaGeneralViewSimple, ReporteAsistenciaEstudianteViewSimple, ReporteAsistenciaCursoViewSimple, ListaEstudiantesViewSimple, ReporteAsistenciaAsignaturasCursoViewSimple, ReporteEvaluacionesAsignaturasCursoViewSimple, ReporteEvaluacionesGeneralViewSimple, ReporteEvaluacionesEstudianteViewSimple
from Core.views import foro as foro_views
from Core.views import pdf_views as pdf_views
from Core.views import cursos as curso_views
from .views.cursos import *
from .views.docentes import (
    ObtenerAsistenciaAsignaturaView,
    ObtenerHistorialAsistenciaView,
    GuardarAsistenciaView,
    ProfesorPanelView,
    ProfesorPanelModularView
)
from .views.alumnos import *
from .views.admin import *
from .views.auth import *
from .views.comunicaciones import *
from .views.foro import *
from .views.usuarios import *
from Core.views import chat
from Core.views.chat import ChatIAView
from .views.docentes import GenerarEvaluacionBaseView, CrearEvaluacionEspecificaView, CrearEvaluacionesEstudiantesView, ObtenerEvaluacionesAsignaturaView, ObtenerNotasEvaluacionView, ActualizarNotaView, EliminarNotaView, ObtenerClasesDocenteView
from Core.views.pdf_views import DescargarAnalisisIAPDFView

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
    path('estudiante/<int:estudiante_id>/detalle/', EstudianteDetalleView.as_view(), name='estudiante_detalle'),

    # URLs para el Foro
    path('foro/', include('Core.urls_foro')),

    # URLs para Comunicaciones
    path('comunicaciones/', include('Core.urls_comunicaciones')),
    
    # URLs para descarga de PDFs
    path('pdf/horario/', pdf_views.DescargarHorarioPDFView.as_view(), name='descargar_horario_pdf'),
    path('pdf/asistencia/', pdf_views.DescargarAsistenciaPDFView.as_view(), name='descargar_asistencia_pdf'),
    path('pdf/calificaciones/', pdf_views.DescargarCalificacionesPDFView.as_view(), name='descargar_calificaciones_pdf'),
    path('pdf/reporte-cursos/', pdf_views.DescargarReporteCursosPDFView.as_view(), name='descargar_reporte_cursos_pdf'),
    path('pdf/reporte-asistencia/', pdf_views.DescargarReporteAsistenciaPDFView.as_view(), name='descargar_reporte_asistencia_pdf'),
    path('pdf/reporte-asistencia-estudiante/', pdf_views.DescargarAsistenciaEstudiantePDFView.as_view(), name='descargar_asistencia_estudiante_pdf'),
    path('pdf/reporte-asistencia-curso/', pdf_views.DescargarAsistenciaCursoPDFView.as_view(), name='descargar_asistencia_curso_pdf'),
    path('pdf/reporte-estudiantes-riesgo/', pdf_views.DescargarReporteEstudiantesRiesgoPDFView.as_view(), name='descargar_reporte_estudiantes_riesgo_pdf'),
    path('pdf/asistencia-estudiante-admin/', pdf_views.DescargarAsistenciaEstudianteAdminPDFView.as_view(), name='descargar_asistencia_estudiante_admin_pdf'),
    path('pdf/promedio-asignaturas-curso/', pdf_views.DescargarPromedioAsignaturasCursoPDFView.as_view(), name='descargar_promedio_asignaturas_curso_pdf'),
    path('pdf/asistencia-asignaturas-curso/', pdf_views.DescargarAsistenciaAsignaturasCursoPDFView.as_view(), name='descargar_asistencia_asignaturas_curso_pdf'),
    path('pdf/evaluaciones-asignaturas-curso/', pdf_views.DescargarEvaluacionesAsignaturasCursoPDFView.as_view(), name='descargar_evaluaciones_asignaturas_curso_pdf'),
    path('pdf/evaluaciones-estudiante-admin/', pdf_views.DescargarEvaluacionesEstudianteAdminPDFView.as_view(), name='descargar_evaluaciones_estudiante_admin_pdf'),
    path('pdf/reporte-evaluaciones-general/', pdf_views.DescargarReporteEvaluacionesGeneralPDFView.as_view(), name='descargar_reporte_evaluaciones_general_pdf'),
    path('pdf/reporte-evaluaciones-asignaturas-docente/', pdf_views.DescargarReporteEvaluacionesAsignaturasDocentePDFView.as_view(), name='descargar_reporte_evaluaciones_asignaturas_docente_pdf'),
    path('pdf/reporte-evaluaciones-curso-jefe/', pdf_views.DescargarReporteEvaluacionesCursoJefePDFView.as_view(), name='descargar_reporte_evaluaciones_curso_jefe_pdf'),
    path('pdf/reporte-asistencia-asignaturas-docente/', pdf_views.DescargarReporteAsistenciaAsignaturasDocentePDFView.as_view(), name='descargar_reporte_asistencia_asignaturas_docente_pdf'),
    path('pdf/reporte-asistencia-curso-jefe/', pdf_views.DescargarReporteAsistenciaCursoJefePDFView.as_view(), name='descargar_reporte_asistencia_curso_jefe_pdf'),
    path('pdf/analisis-ia/', DescargarAnalisisIAPDFView.as_view(), name='descargar_analisis_ia_pdf'),
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
    path('obtener-asistencia-asignatura/<int:asignatura_id>/', ObtenerAsistenciaAsignaturaView.as_view(), name='obtener_asistencia_asignatura'),
    path('guardar-asistencia/<int:clase_id>/', GuardarAsistenciaView.as_view(), name='guardar_asistencia'),
    
    # URLs para eventos del calendario (docentes) - COMENTADAS TEMPORALMENTE
    # path('crear-evento-calendario/', CrearEventoCalendarioView.as_view(), name='crear_evento_calendario'),
    # path('editar-evento-calendario/<int:evento_id>/', EditarEventoCalendarioView.as_view(), name='editar_evento_calendario'),
    # path('eliminar-evento-calendario/<int:evento_id>/', EliminarEventoCalendarioView.as_view(), name='eliminar_evento_calendario'),
    
    # URLs para eventos del calendario (administrador)
    path('admin-eventos-calendario/', AdminEventosCalendarioView.as_view(), name='admin_eventos_calendario'),
    path('admin-crear-evento-calendario/', AdminCrearEventoCalendarioView.as_view(), name='admin_crear_evento_calendario'),
    path('admin-detalle-evento-calendario/<str:evento_id>/', AdminDetalleEventoCalendarioView.as_view(), name='admin_detalle_evento_calendario'),
    path('admin-editar-evento-calendario/<str:evento_id>/', AdminEditarEventoCalendarioView.as_view(), name='admin_editar_evento_calendario'),
    path('admin-eliminar-evento-calendario/<str:evento_id>/', AdminEliminarEventoCalendarioView.as_view(), name='admin_eliminar_evento_calendario'),
    
    # APIs para formularios
    path('api/cursos/', ApiCursosView.as_view(), name='api_cursos'),
    path('api/asignaturas/', ApiAsignaturasView.as_view(), name='api_asignaturas'),
    
    # URLs para gestión de cursos
    path('cursos/<int:curso_id>/data/', CursoDataView.as_view(), name='curso_data'),
    path('cursos/<int:curso_id>/update/', CursoUpdateView.as_view(), name='curso_update'),
    path('cursos/<int:curso_id>/delete/', CursoDeleteView.as_view(), name='curso_delete'),
    
    # URLs para gestión de asignaturas
    path('asignaturas/create/', AsignaturaCreateView.as_view(), name='asignatura_create'),
    path('asignaturas/<int:asignatura_id>/data/', AsignaturaDataView.as_view(), name='asignatura_data'),
    path('asignaturas/<int:asignatura_id>/update/', AsignaturaUpdateView.as_view(), name='asignatura_update'),
    path('asignaturas/<int:asignatura_id>/delete/', AsignaturaDeleteView.as_view(), name='asignatura_delete'),
    
    # URLs para reportes del admin
    path('api/dashboard-metricas/', DashboardMetricasView.as_view(), name='dashboard_metricas'),
    path('api/reporte-rendimiento-cursos/', ReporteRendimientoCursosViewSimple.as_view(), name='reporte_rendimiento_cursos'),
    path('api/reporte-asistencia-general/', ReporteAsistenciaGeneralView.as_view(), name='reporte_asistencia_general'),
    path('api/reporte-asistencia-cursos/', ReporteAsistenciaGeneralViewSimple.as_view(), name='reporte_asistencia_cursos'),
    path('api/reporte-asistencia-estudiante/', ReporteAsistenciaEstudianteViewSimple.as_view(), name='reporte_asistencia_estudiante'),
    path('api/reporte-asistencia-curso/', ReporteAsistenciaCursoViewSimple.as_view(), name='reporte_asistencia_curso'),
    path('api/reporte-asistencia-asignaturas-curso/', ReporteAsistenciaAsignaturasCursoViewSimple.as_view(), name='reporte_asistencia_asignaturas_curso'),
    path('api/reporte-evaluaciones-asignaturas-curso/', ReporteEvaluacionesAsignaturasCursoViewSimple.as_view(), name='reporte_evaluaciones_asignaturas_curso'),
    path('api/reporte-evaluaciones-general/', ReporteEvaluacionesGeneralViewSimple.as_view(), name='reporte_evaluaciones_general'),
    path('api/reporte-evaluaciones-estudiante/', ReporteEvaluacionesEstudianteViewSimple.as_view(), name='reporte_evaluaciones_estudiante'),
    path('api/lista-estudiantes/', ListaEstudiantesViewSimple.as_view(), name='lista_estudiantes'),
    path('api/reporte-docentes/', ReporteDocentesViewSimple.as_view(), name='reporte_docentes'),
    path('api/reporte-estudiantes-riesgo/', ReporteEstudiantesRiesgoViewSimple.as_view(), name='reporte_estudiantes_riesgo'),
    path('api/reporte-evaluaciones/', ReporteEvaluacionesView.as_view(), name='reporte_evaluaciones'),
    
    # URLs para reportes de docentes
    path('api/reporte-evaluaciones-asignaturas-docente/', ReporteEvaluacionesAsignaturasDocenteView.as_view(), name='reporte_evaluaciones_asignaturas_docente'),
    path('api/reporte-evaluaciones-curso-jefe/', ReporteEvaluacionesCursoJefeView.as_view(), name='reporte_evaluaciones_curso_jefe'),
    path('api/reporte-asistencia-asignaturas-docente/', ReporteAsistenciaAsignaturasDocenteView.as_view(), name='reporte_asistencia_asignaturas_docente'),
    path('api/reporte-asistencia-curso-jefe/', ReporteAsistenciaCursoJefeView.as_view(), name='reporte_asistencia_curso_jefe'),
    path('api/resumen-general-docente/', ResumenGeneralDocenteView.as_view(), name='resumen_general_docente'),
]

urlpatterns += [
    # Chat público (versión de prueba)
    path('chat/', chat.ChatPublicoView.as_view(), name='chat_gem'),
]

urlpatterns += [
    # URLs para análisis IA
    path('api/curso/<int:curso_id>/analisis-rendimiento/', curso_views.analisis_rendimiento, name='analisis_rendimiento'),
    path('api/curso/<int:curso_id>/prediccion-riesgo/', curso_views.prediccion_riesgo, name='prediccion_riesgo'),
    path('api/curso/<int:curso_id>/recomendaciones/', curso_views.obtener_recomendaciones, name='obtener_recomendaciones'),
    path('api/generar-pdf/', curso_views.generar_pdf, name='generar_pdf'),
]

urlpatterns += [
    # Comunicaciones
    path('comunicacion/<int:comunicacion_id>/eliminar/', curso_views.EliminarComunicacionView.as_view(), name='eliminar_comunicacion'),
]

urlpatterns += [
    # URLs del foro de asignatura
    path('asignatura/<int:asignatura_id>/foro/', curso_views.ForoAsignaturaView.as_view(), name='foro_asignatura'),
    path('asignatura/<int:asignatura_id>/foro/tema/<int:tema_id>/', curso_views.TemaForoAsignaturaView.as_view(), name='tema_foro_asignatura'),
]

urlpatterns += [
    # URLs para chat IA
    path('api/chat-ia/', ChatIAView.as_view(), name='chat_ia'),
]

urlpatterns += [
    # URLs de asistencia
    path('obtener-historial-asistencia/<int:asignatura_id>/', ObtenerHistorialAsistenciaView.as_view(), name='obtener_historial_asistencia'),
]

urlpatterns += [
    # URLs para el sistema de notas y evaluaciones
    path('api/evaluacion-base/<int:asignatura_id>/generar/', 
         GenerarEvaluacionBaseView.as_view(), name='generar_evaluacion_base'),
    path('api/evaluacion-especifica/crear/', 
         CrearEvaluacionEspecificaView.as_view(), name='crear_evaluacion_especifica'),
    path('api/evaluacion/<int:evaluacion_id>/estudiantes/crear/', 
         CrearEvaluacionesEstudiantesView.as_view(), name='crear_evaluaciones_estudiantes'),
    path('api/asignatura/<int:asignatura_id>/evaluaciones/', 
         ObtenerEvaluacionesAsignaturaView.as_view(), name='obtener_evaluaciones_asignatura'),
    path('api/evaluacion/<int:evaluacion_id>/notas/', 
         ObtenerNotasEvaluacionView.as_view(), name='obtener_notas_evaluacion'),
    path('api/nota/<int:nota_id>/actualizar/', 
         ActualizarNotaView.as_view(), name='actualizar_nota'),
    path('api/nota/<int:nota_id>/eliminar/', 
         EliminarNotaView.as_view(), name='eliminar_nota'),
    path('api/asignatura/<int:asignatura_id>/clases/', 
         ObtenerClasesDocenteView.as_view(), name='obtener_clases_asignatura'),
]

urlpatterns += [
    # URLs para obtener clases del docente
    path('api/clases-docente/<int:docente_id>/', ObtenerClasesDocenteView.as_view(), name='obtener_clases_docente'),
]

