from django.urls import path
from .views import (
    HomeView, AdminPanelView, UserManagementView, UserCreateView,
    UserDetailView, UserUpdateView, UserDeleteView, ProfesorPanelView,
    EstudiantePanelView, AttendanceView, LoginView, LogoutView,
    ChangePasswordView
)

urlpatterns = [
    # URLs de autenticación
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # URLs existentes
    path('', HomeView.as_view(), name='home'),
    path('admin-panel/', AdminPanelView.as_view(), name='admin_panel'),
    path('users/', UserManagementView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:user_id>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:user_id>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('profesor-panel/', ProfesorPanelView.as_view(), name='profesor_panel'),
    path('estudiante-panel/', EstudiantePanelView.as_view(), name='estudiante_panel'),
    path('attendance/', AttendanceView.as_view(), name='attendance'),
]

