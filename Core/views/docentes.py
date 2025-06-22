from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from Core.models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura, AsignaturaImpartida, Curso, ProfesorJefe
from django.db.models import Count, Avg
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.db import transaction
from Core.servicios.repos import usuarios
from Core.servicios.helpers import validadores, serializadores

@method_decorator(login_required, name='dispatch')
class ProfesorPanelView(View):
    def get(self, request):
        if not hasattr(request.user.usuario, 'docente'):
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        
        docente = request.user.usuario.docente
        
        # Obtener cursos donde el docente es profesor jefe
        cursos_profesor_jefe = Curso.objects.filter(
            jefatura_actual__docente=docente
        ).select_related('jefatura_actual__docente__usuario').annotate(
            total_estudiantes=Count('estudiantes')
        )
        
        # Obtener asignaturas que imparte el docente
        asignaturas = AsignaturaImpartida.objects.filter(
            docente=docente
        ).select_related(
            'asignatura',
            'docente__usuario'
        ).prefetch_related('clases')
        
        context = {
            'cursos_profesor_jefe': cursos_profesor_jefe,
            'asignaturas': asignaturas
        }
        return render(request, 'teacher_panel.html', context)

@method_decorator(login_required, name='dispatch')
class ProfesorPanelModularView(View):
    def get(self, request):
        if not hasattr(request.user.usuario, 'docente'):
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        
        docente = request.user.usuario.docente
        
        # Obtener cursos donde el docente es profesor jefe
        cursos_profesor_jefe = Curso.objects.filter(
            jefatura_actual__docente=docente
        ).select_related('jefatura_actual__docente__usuario').annotate(
            total_estudiantes=Count('estudiantes')
        )
        
        # Obtener asignaturas que imparte el docente
        asignaturas = AsignaturaImpartida.objects.filter(
            docente=docente
        ).select_related(
            'asignatura',
            'docente__usuario'
        ).prefetch_related('clases')
        
        context = {
            'cursos_profesor_jefe': cursos_profesor_jefe,
            'asignaturas': asignaturas
        }
        return render(request, 'teacher_panel_modular.html', context)

