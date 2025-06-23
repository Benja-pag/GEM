from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from Core.models import Estudiante
from Core.views.alumnos import get_horario_estudiante, get_asistencia_estudiante, get_evaluaciones_estudiante, get_promedio_estudiante
from .pdf_generators import generar_pdf_horario, generar_pdf_asistencia, generar_pdf_calificaciones

@method_decorator(login_required, name='dispatch')
class DescargarHorarioPDFView(View):
    """
    Vista para descargar el horario del estudiante en PDF
    """
    def get(self, request):
        # Verificar que el usuario es un estudiante
        if not hasattr(request.user.usuario, 'estudiante'):
            return HttpResponse('No tienes permiso para acceder a esta página', status=403)
        
        estudiante = request.user.usuario.estudiante
        
        # Obtener datos del horario
        horario_data = get_horario_estudiante(request.user.id)
        
        # Generar PDF
        buffer = generar_pdf_horario(estudiante, horario_data)
        
        # Crear respuesta HTTP
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="horario_{estudiante.usuario.nombre}_{estudiante.usuario.apellido_paterno}.pdf"'
        
        return response

@method_decorator(login_required, name='dispatch')
class DescargarAsistenciaPDFView(View):
    """
    Vista para descargar el reporte de asistencia del estudiante en PDF
    """
    def get(self, request):
        # Verificar que el usuario es un estudiante
        if not hasattr(request.user.usuario, 'estudiante'):
            return HttpResponse('No tienes permiso para acceder a esta página', status=403)
        
        estudiante = request.user.usuario.estudiante
        
        # Obtener datos de asistencia
        asistencia_data = get_asistencia_estudiante(estudiante.pk)
        
        # Generar PDF
        buffer = generar_pdf_asistencia(estudiante, asistencia_data)
        
        # Crear respuesta HTTP
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="asistencia_{estudiante.usuario.nombre}_{estudiante.usuario.apellido_paterno}.pdf"'
        
        return response

@method_decorator(login_required, name='dispatch')
class DescargarCalificacionesPDFView(View):
    """
    Vista para descargar el reporte de calificaciones del estudiante en PDF
    """
    def get(self, request):
        # Verificar que el usuario es un estudiante
        if not hasattr(request.user.usuario, 'estudiante'):
            return HttpResponse('No tienes permiso para acceder a esta página', status=403)
        
        estudiante = request.user.usuario.estudiante
        
        # Obtener datos de calificaciones
        calificaciones_data = get_evaluaciones_estudiante(estudiante.pk)
        promedio = get_promedio_estudiante(estudiante.pk)
        
        # Generar PDF
        buffer = generar_pdf_calificaciones(estudiante, calificaciones_data, promedio)
        
        # Crear respuesta HTTP
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="calificaciones_{estudiante.usuario.nombre}_{estudiante.usuario.apellido_paterno}.pdf"'
        
        return response 