from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TemaViewSet, ComentarioViewSet, ReaccionViewSet

router = DefaultRouter()
router.register(r'temas', TemaViewSet)
router.register(r'comentarios', ComentarioViewSet)
router.register(r'reacciones', ReaccionViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 