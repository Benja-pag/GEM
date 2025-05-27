from rest_framework import serializers
from .models import Evento, Recordatorio
from apps.users.serializers import UserSerializer
from apps.subjects.serializers import AsignaturaSerializer

class EventoSerializer(serializers.ModelSerializer):
    creador = UserSerializer(read_only=True)
    participantes = UserSerializer(many=True, read_only=True)
    asignatura = AsignaturaSerializer(read_only=True)

    class Meta:
        model = Evento
        fields = '__all__'

class RecordatorioSerializer(serializers.ModelSerializer):
    evento = EventoSerializer(read_only=True)
    usuario = UserSerializer(read_only=True)

    class Meta:
        model = Recordatorio
        fields = '__all__' 