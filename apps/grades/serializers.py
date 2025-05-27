from rest_framework import serializers
from .models import Calificacion, Promedio
from apps.users.serializers import UserSerializer
from apps.subjects.serializers import AsignaturaSerializer

class CalificacionSerializer(serializers.ModelSerializer):
    alumno = UserSerializer(read_only=True)
    asignatura = AsignaturaSerializer(read_only=True)

    class Meta:
        model = Calificacion
        fields = '__all__'

class PromedioSerializer(serializers.ModelSerializer):
    alumno = UserSerializer(read_only=True)
    asignatura = AsignaturaSerializer(read_only=True)

    class Meta:
        model = Promedio
        fields = '__all__' 