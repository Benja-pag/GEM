from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Clase, Sala
from .services import ClassService
from .serializers import ClaseSerializer, SalaSerializer

class ClassViewSet(viewsets.ModelViewSet):
    queryset = Clase.objects.all()
    serializer_class = ClaseSerializer
    service = ClassService()

    def create(self, request, *args, **kwargs):
        try:
            clase = self.service.create_class(
                nombre=request.data.get('nombre'),
                curso=request.data.get('curso'),
                profesor_jefe=request.data.get('profesor_jefe')
            )
            serializer = self.get_serializer(clase)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        """Agrega un estudiante a la clase"""
        try:
            student_id = request.data.get('student_id')
            clase = self.service.add_student_to_class(pk, student_id)
            serializer = self.get_serializer(clase)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def remove_student(self, request, pk=None):
        """Elimina un estudiante de la clase"""
        try:
            student_id = request.data.get('student_id')
            clase = self.service.remove_student_from_class(pk, student_id)
            serializer = self.get_serializer(clase)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def teacher_classes(self, request):
        """Obtiene todas las clases de un profesor"""
        try:
            teacher_id = request.query_params.get('teacher_id')
            classes = self.service.get_teacher_classes(teacher_id)
            serializer = self.get_serializer(classes, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def student_classes(self, request):
        """Obtiene todas las clases de un estudiante"""
        try:
            student_id = request.query_params.get('student_id')
            classes = self.service.get_student_classes(student_id)
            serializer = self.get_serializer(classes, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Sala.objects.all()
    serializer_class = SalaSerializer
    service = ClassService()

    def create(self, request, *args, **kwargs):
        try:
            sala = self.service.create_room(
                nombre=request.data.get('nombre'),
                capacidad=request.data.get('capacidad'),
                ubicacion=request.data.get('ubicacion')
            )
            serializer = self.get_serializer(sala)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 