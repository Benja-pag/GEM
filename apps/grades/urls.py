from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GradeViewSet, PromedioViewSet

router = DefaultRouter()
router.register(r'grades', GradeViewSet)
router.register(r'averages', PromedioViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 