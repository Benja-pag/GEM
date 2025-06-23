from django.urls import path
from .views import foro as foro_views

urlpatterns = [
    path('', foro_views.ForoGeneralView.as_view(), name='foro_general'),
    path('tema/nuevo/', foro_views.CrearTemaForoView.as_view(), name='crear_tema_foro'),
    path('tema/<int:tema_id>/', foro_views.TemaForoView.as_view(), name='ver_tema_foro'),
] 