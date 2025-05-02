from django.urls import path, include  # Asegúrate de importar include
from .views import (
    HomeView,
    AdminPanelView,
    ProfesorPanelView,  # IMPORTA LA VISTA 'ProfesorPanelView'
    EstudiantePanelView,  # IMPORTA LA VISTA 'EstudiantePanelView'
    UserManagementView,
    UserCreateView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
    CursoCreateView,
    CursoUpdateView,
    CursoDeleteView,
    CursoDetailView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('admin-panel/', AdminPanelView.as_view(), name='admin_panel'),
    path('profesor-panel/', ProfesorPanelView.as_view(), name='profesor_panel'),
    path('estudiante-panel/', EstudiantePanelView.as_view(), name='estudiante_panel'),
    
    # URLs de usuarios
    path('users/', UserManagementView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:user_id>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:user_id>/delete/', UserDeleteView.as_view(), name='user_delete'),
    
    # URLs de cursos
    path('cursos/create/', CursoCreateView.as_view(), name='curso_create'),
    path('cursos/<int:curso_id>/', CursoDetailView.as_view(), name='curso_detail'),
    path('cursos/<int:curso_id>/update/', CursoUpdateView.as_view(), name='curso_update'),
    path('cursos/<int:curso_id>/delete/', CursoDeleteView.as_view(), name='curso_delete'),
]

