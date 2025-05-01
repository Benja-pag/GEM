from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('admin-panel/usuarios/<int:id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('admin-panel/usuarios/<int:id>/cambiar-estado/', views.cambiar_estado_usuario, name='cambiar_estado_usuario'),
]
