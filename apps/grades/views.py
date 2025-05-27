from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Calificacion, Promedio
from .services import GradeService
from .serializers import CalificacionSerializer, PromedioSerializer

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Calificacion.objects.all()
    serializer_class = CalificacionSerializer
    service = GradeService()

    def create(self, request, *args, **kwargs):
        try:
            calificacion = self.service.create_grade(
                alumno=request.data.get('alumno'),
                asignatura=request.data.get('asignatura'),
                nota=request.data.get('nota'),
                fecha=request.data.get('fecha'),
                tipo=request.data.get('tipo'),
                comentario=request.data.get('comentario')
            )
            serializer = self.get_serializer(calificacion)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def student_grades(self, request):
        """Obtiene todas las calificaciones de un estudiante"""
        try:
            student_id = request.query_params.get('student_id')
            subject_id = request.query_params.get('subject_id')
            grades = self.service.get_student_grades(student_id, subject_id)
            serializer = self.get_serializer(grades, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def subject_grades(self, request):
        """Obtiene todas las calificaciones de una asignatura"""
        try:
            subject_id = request.query_params.get('subject_id')
            grades = self.service.get_subject_grades(subject_id)
            serializer = self.get_serializer(grades, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PromedioViewSet(viewsets.ModelViewSet):
    queryset = Promedio.objects.all()
    serializer_class = PromedioSerializer
    service = GradeService()

    @action(detail=False, methods=['post'])
    def calculate_average(self, request):
        """Calcula el promedio de un alumno en una asignatura"""
        try:
            promedio = self.service.calculate_average(
                alumno=request.data.get('alumno'),
                asignatura=request.data.get('asignatura'),
                periodo=request.data.get('periodo')
            )
            serializer = self.get_serializer(promedio)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def student_averages(self, request):
        """Obtiene todos los promedios de un estudiante"""
        try:
            student_id = request.query_params.get('student_id')
            subject_id = request.query_params.get('subject_id')
            averages = self.service.get_student_averages(student_id, subject_id)
            serializer = self.get_serializer(averages, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 