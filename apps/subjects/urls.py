from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AsignaturaViewSet, ElectivoViewSet

router = DefaultRouter()
router.register(r'asignaturas', AsignaturaViewSet)
router.register(r'electivos', ElectivoViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 