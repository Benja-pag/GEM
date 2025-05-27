from rest_framework import serializers
from apps.users.serializers import UserSerializer
from apps.classes.serializers import ClaseSerializer
from .models import Asignatura, Electivo

class AsignaturaSerializer(serializers.ModelSerializer):
    docente = UserSerializer(read_only=True)
    clase = ClaseSerializer(read_only=True)

    class Meta:
        model = Asignatura
        fields = [
            'id', 'nombre', 'codigo', 'dia', 'horario',
            'docente', 'clase', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ElectivoSerializer(serializers.ModelSerializer):
    profesor = UserSerializer(read_only=True)
    asignatura = AsignaturaSerializer(read_only=True)

    class Meta:
        model = Electivo
        fields = [
            'id', 'nombre', 'asignatura', 'profesor', 'sala',
            'dia', 'hora_inicio', 'hora_fin', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at'] 