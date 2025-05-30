from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from Core.models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura
from django.db.models import Count, Avg
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
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
from Core.servicios.repos.asignaturas import get_asignaturas_estudiante
from Core.servicios.repos.cursos import get_estudiantes_por_curso

@method_decorator(login_required, name='dispatch')
class EstudiantePanelView(View):
    def get(self, request):
        if not hasattr(request.user.usuario, 'estudiante'):
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        usuario = request.user.usuario
        # notas = Nota.objects.filter(estudiante=estudiante)
        # asistencias = Asistencia.objects.filter(estudiante=estudiante)
        curso = usuario.estudiante.curso
        estudiantes_curso = get_estudiantes_por_curso(usuario.estudiante.curso_id)
        asignaturas_estudiante = get_asignaturas_estudiante(usuario.pk)  
        
        context = {
            # 'notas': notas,
            # 'asistencias': asistencias,
            'curso' : curso,
            'estudiantes_curso': estudiantes_curso,
            'asignaturas_estudiante': asignaturas_estudiante
        }
        
        return render(request, 'student_panel.html', context)



@method_decorator(login_required, name='dispatch')
class AttendanceView(TemplateView):
    template_name = 'attendance.html'
    
    def get(self, request, *args, **kwargs):
        if not (request.user.is_admin or hasattr(request.user.usuario, 'docente')):
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        return super().get(request, *args, **kwargs)

