from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Asistencia, RegistroAsistencia
from .services import AttendanceService
from .serializers import AsistenciaSerializer, RegistroAsistenciaSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Asistencia.objects.all()
    serializer_class = AsistenciaSerializer
    service = AttendanceService()

    def create(self, request, *args, **kwargs):
        try:
            asistencia = self.service.create_attendance(
                alumno=request.data.get('alumno'),
                asignatura=request.data.get('asignatura'),
                fecha=request.data.get('fecha'),
                estado=request.data.get('estado'),
                justificacion=request.data.get('justificacion')
            )
            serializer = self.get_serializer(asistencia)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def student_attendance(self, request):
        """Obtiene los registros de asistencia de un estudiante"""
        try:
            student_id = request.query_params.get('student_id')
            subject_id = request.query_params.get('subject_id')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            attendances = self.service.get_student_attendance(
                student_id, subject_id, start_date, end_date
            )
            serializer = self.get_serializer(attendances, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def subject_attendance(self, request):
        """Obtiene los registros de asistencia de una asignatura"""
        try:
            subject_id = request.query_params.get('subject_id')
            date = request.query_params.get('date')
            attendances = self.service.get_subject_attendance(subject_id, date)
            serializer = self.get_serializer(attendances, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'])
    def update_attendance(self, request, pk=None):
        """Actualiza un registro de asistencia"""
        try:
            asistencia = self.service.update_attendance(
                pk,
                estado=request.data.get('estado'),
                justificacion=request.data.get('justificacion')
            )
            serializer = self.get_serializer(asistencia)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = RegistroAsistencia.objects.all()
    serializer_class = RegistroAsistenciaSerializer
    service = AttendanceService()

    def create(self, request, *args, **kwargs):
        try:
            registro = self.service.create_attendance_record(
                asignatura=request.data.get('asignatura'),
                fecha=request.data.get('fecha'),
                profesor=request.data.get('profesor'),
                observaciones=request.data.get('observaciones')
            )
            serializer = self.get_serializer(registro)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def attendance_records(self, request):
        """Obtiene los registros de asistencia de las clases"""
        try:
            subject_id = request.query_params.get('subject_id')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            records = self.service.get_attendance_records(
                subject_id, start_date, end_date
            )
            serializer = self.get_serializer(records, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 