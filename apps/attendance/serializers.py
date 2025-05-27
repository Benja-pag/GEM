from rest_framework import serializers
from .models import Asistencia, RegistroAsistencia
from apps.users.serializers import UserSerializer
from apps.subjects.serializers import AsignaturaSerializer

class AsistenciaSerializer(serializers.ModelSerializer):
    alumno = UserSerializer(read_only=True)
    asignatura = AsignaturaSerializer(read_only=True)

    class Meta:
        model = Asistencia
        fields = '__all__'

class RegistroAsistenciaSerializer(serializers.ModelSerializer):
    asignatura = AsignaturaSerializer(read_only=True)
    profesor = UserSerializer(read_only=True)

    class Meta:
        model = RegistroAsistencia
        fields = '__all__' 