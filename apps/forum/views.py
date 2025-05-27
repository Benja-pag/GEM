from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Tema, Comentario, Reaccion
from .serializers import TemaSerializer, ComentarioSerializer, ReaccionSerializer
from .services import ForumService

class TemaViewSet(viewsets.ModelViewSet):
    queryset = Tema.objects.all()
    serializer_class = TemaSerializer

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                tema = ForumService.create_tema(
                    titulo=request.data.get('titulo'),
                    descripcion=request.data.get('descripcion'),
                    asignatura_id=request.data.get('asignatura'),
                    creador=request.user
                )
                serializer = self.get_serializer(tema)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        tema = self.get_object()
        try:
            tema = ForumService.close_tema(tema)
            serializer = self.get_serializer(tema)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def active(self, request):
        asignatura_id = request.query_params.get('asignatura')
        temas = ForumService.get_temas_activos(asignatura_id)
        serializer = self.get_serializer(temas, many=True)
        return Response(serializer.data)

class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                comentario = ForumService.create_comentario(
                    tema_id=request.data.get('tema'),
                    autor=request.user,
                    contenido=request.data.get('contenido')
                )
                serializer = self.get_serializer(comentario)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def reactions(self, request, pk=None):
        comentario = self.get_object()
        reacciones = ForumService.get_reacciones_comentario(comentario)
        serializer = ReaccionSerializer(reacciones, many=True)
        return Response(serializer.data)

class ReaccionViewSet(viewsets.ModelViewSet):
    queryset = Reaccion.objects.all()
    serializer_class = ReaccionSerializer

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                reaccion = ForumService.add_reaccion(
                    comentario_id=request.data.get('comentario'),
                    usuario=request.user,
                    tipo=request.data.get('tipo')
                )
                serializer = self.get_serializer(reaccion)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 