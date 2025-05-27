from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventoViewSet, RecordatorioViewSet

router = DefaultRouter()
router.register(r'events', EventoViewSet)
router.register(r'reminders', RecordatorioViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 