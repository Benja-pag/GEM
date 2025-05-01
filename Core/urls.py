from django.urls import path, include
from .views import (
    HomeView,
    AdminPanelView,
    UserCreateView,
    UserUpdateView,
    UserDeleteView,
    AttendanceView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('admin-panel/', AdminPanelView.as_view(), name='admin_panel'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:user_id>/', UserUpdateView.as_view(), name='user_detail'),
    path('users/<int:user_id>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:user_id>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('asistencia/', AttendanceView.as_view(), name='attendance'),
]
