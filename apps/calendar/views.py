from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Evento, Recordatorio
from .services import CalendarService
from .serializers import EventoSerializer, RecordatorioSerializer

class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    service = CalendarService()

    def create(self, request, *args, **kwargs):
        try:
            evento = self.service.create_event(
                titulo=request.data.get('titulo'),
                descripcion=request.data.get('descripcion'),
                tipo=request.data.get('tipo'),
                fecha_inicio=request.data.get('fecha_inicio'),
                fecha_fin=request.data.get('fecha_fin'),
                asignatura=request.data.get('asignatura'),
                creador=request.data.get('creador'),
                participantes=request.data.get('participantes')
            )
            serializer = self.get_serializer(evento)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def user_events(self, request):
        """Obtiene los eventos de un usuario"""
        try:
            user_id = request.query_params.get('user_id')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            tipo = request.query_params.get('tipo')
            eventos = self.service.get_user_events(user_id, start_date, end_date, tipo)
            serializer = self.get_serializer(eventos, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def subject_events(self, request):
        """Obtiene los eventos de una asignatura"""
        try:
            subject_id = request.query_params.get('subject_id')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            eventos = self.service.get_subject_events(subject_id, start_date, end_date)
            serializer = self.get_serializer(eventos, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class RecordatorioViewSet(viewsets.ModelViewSet):
    queryset = Recordatorio.objects.all()
    serializer_class = RecordatorioSerializer
    service = CalendarService()

    def create(self, request, *args, **kwargs):
        try:
            recordatorio = self.service.create_reminder(
                evento=request.data.get('evento'),
                usuario=request.data.get('usuario'),
                tiempo_antes=request.data.get('tiempo_antes')
            )
            serializer = self.get_serializer(recordatorio)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def pending_reminders(self, request):
        """Obtiene los recordatorios pendientes"""
        try:
            recordatorios = self.service.get_pending_reminders()
            serializer = self.get_serializer(recordatorios, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def mark_sent(self, request, pk=None):
        """Marca un recordatorio como enviado"""
        try:
            recordatorio = self.service.mark_reminder_sent(pk)
            serializer = self.get_serializer(recordatorio)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 