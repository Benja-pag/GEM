from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Asignatura, Electivo
from .serializers import AsignaturaSerializer, ElectivoSerializer
from .services import ServicioAsignatura

class AsignaturaViewSet(viewsets.ModelViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer
    service = ServicioAsignatura()

    def create(self, request, *args, **kwargs):
        try:
            asignatura = self.service.crear_asignatura(
                nombre=request.data.get('nombre'),
                codigo=request.data.get('codigo'),
                dia=request.data.get('dia'),
                horario=request.data.get('horario'),
                docente_id=request.data.get('docente'),
                clase_id=request.data.get('clase')
            )
            serializer = self.get_serializer(asignatura)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def por_docente(self, request):
        """Obtiene las asignaturas de un docente"""
        try:
            docente_id = request.query_params.get('docente_id')
            asignaturas = self.service.obtener_asignaturas_docente(docente_id)
            serializer = self.get_serializer(asignaturas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def por_clase(self, request):
        """Obtiene las asignaturas de una clase"""
        try:
            clase_id = request.query_params.get('clase_id')
            asignaturas = self.service.obtener_asignaturas_clase(clase_id)
            serializer = self.get_serializer(asignaturas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ElectivoViewSet(viewsets.ModelViewSet):
    queryset = Electivo.objects.all()
    serializer_class = ElectivoSerializer
    service = ServicioAsignatura()

    def create(self, request, *args, **kwargs):
        try:
            electivo = self.service.crear_electivo(
                nombre=request.data.get('nombre'),
                asignatura_id=request.data.get('asignatura'),
                profesor_id=request.data.get('profesor'),
                sala=request.data.get('sala'),
                dia=request.data.get('dia'),
                hora_inicio=request.data.get('hora_inicio'),
                hora_fin=request.data.get('hora_fin')
            )
            serializer = self.get_serializer(electivo)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def por_profesor(self, request):
        """Obtiene los electivos de un profesor"""
        try:
            profesor_id = request.query_params.get('profesor_id')
            electivos = self.service.obtener_electivos_profesor(profesor_id)
            serializer = self.get_serializer(electivos, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def por_asignatura(self, request):
        """Obtiene los electivos de una asignatura"""
        try:
            asignatura_id = request.query_params.get('asignatura_id')
            electivos = self.service.obtener_electivos_asignatura(asignatura_id)
            serializer = self.get_serializer(electivos, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 