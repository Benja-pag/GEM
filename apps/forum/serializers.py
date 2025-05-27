from rest_framework import serializers
from apps.users.serializers import UserSerializer
from apps.subjects.serializers import AsignaturaSerializer
from .models import Tema, Comentario, Reaccion

class ReaccionSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)

    class Meta:
        model = Reaccion
        fields = ['id', 'usuario', 'tipo', 'created_at', 'updated_at']
        read_only_fields = ['usuario', 'created_at', 'updated_at']

class ComentarioSerializer(serializers.ModelSerializer):
    autor = UserSerializer(read_only=True)
    reacciones = ReaccionSerializer(many=True, read_only=True)

    class Meta:
        model = Comentario
        fields = ['id', 'tema', 'autor', 'contenido', 'reacciones', 'created_at', 'updated_at']
        read_only_fields = ['autor', 'created_at', 'updated_at']

class TemaSerializer(serializers.ModelSerializer):
    creador = UserSerializer(read_only=True)
    participantes = UserSerializer(many=True, read_only=True)
    asignatura = AsignaturaSerializer(read_only=True)
    comentarios = ComentarioSerializer(many=True, read_only=True)

    class Meta:
        model = Tema
        fields = [
            'id', 'titulo', 'descripcion', 'asignatura', 'creador',
            'participantes', 'comentarios', 'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['creador', 'participantes', 'created_at', 'updated_at'] 