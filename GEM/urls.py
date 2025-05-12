"""
URL configuration for GEM project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from Core.views import (
    HomeView, AdminPanelView, UserManagementView, UserCreateView,
    UserDetailView, UserUpdateView, UserDeleteView, ProfesorPanelView,
    EstudiantePanelView, AttendanceView, login_view, LogoutView,
    RegisterView, CreateAdminView, ChangePasswordView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('admin-panel/', AdminPanelView.as_view(), name='admin_panel'),
    path('user-management/', UserManagementView.as_view(), name='user_management'),
    path('user/create/', UserCreateView.as_view(), name='user_create'),
    path('user/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('user/<int:user_id>/update/', UserUpdateView.as_view(), name='user_update'),
    path('user/<int:user_id>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('profesor-panel/', ProfesorPanelView.as_view(), name='profesor_panel'),
    path('estudiante-panel/', EstudiantePanelView.as_view(), name='estudiante_panel'),
    path('attendance/', AttendanceView.as_view(), name='attendance'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('create-admin/', CreateAdminView.as_view(), name='create_admin'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
