from rest_framework import serializers
from .models import Clase, Sala
from apps.users.serializers import UserSerializer

class ClaseSerializer(serializers.ModelSerializer):
    profesor_jefe = UserSerializer(read_only=True)
    alumnos = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Clase
        fields = '__all__'

class SalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = '__all__' 