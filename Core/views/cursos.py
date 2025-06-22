from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from Core.models import Usuario, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura, AsignaturaImpartida, Curso, ProfesorJefe
from django.db.models import Count, Avg
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from Core.servicios.repos import usuarios
from Core.servicios.helpers import validadores, serializadores
from Core.servicios.repos.cursos import get_curso, get_estudiantes_por_curso

@method_decorator(login_required, name='dispatch')
class CursoDetalleView(View):
    def get(self, request, curso_id):
        curso = get_object_or_404(Curso, id=curso_id)
        
        # Obtener estudiantes del curso
        estudiantes = Estudiante.objects.filter(curso=curso).select_related('usuario')
        
        # Obtener asignaturas impartidas en el curso
        asignaturas = AsignaturaImpartida.objects.filter(
            clases__curso=curso
        ).select_related(
            'asignatura',
            'docente__usuario'
        ).distinct()
        
        # Obtener profesor jefe
        profesor_jefe = ProfesorJefe.objects.filter(
            curso=curso
        ).select_related('docente__usuario').first()
        
        context = {
            'curso': curso,
            'estudiantes': estudiantes,
            'asignaturas': asignaturas,
            'profesor_jefe': profesor_jefe
        }
        return render(request, 'teacher/curso_detalle.html', context)

@method_decorator(login_required, name='dispatch')
class AsignaturaDetalleView(View):
    def get(self, request, asignatura_id):
        asignatura = get_object_or_404(AsignaturaImpartida, id=asignatura_id)
        
        # Obtener estudiantes inscritos
        estudiantes = Estudiante.objects.filter(
            asignaturas_inscritas__asignatura_impartida=asignatura,
            asignaturas_inscritas__validada=True
        ).select_related('usuario')
        
        # Obtener clases de la asignatura
        clases = Clase.objects.filter(
            asignatura_impartida=asignatura
        ).order_by('fecha', 'horario')
        
        context = {
            'asignatura': asignatura,
            'estudiantes': estudiantes,
            'clases': clases
        }
        return render(request, 'teacher/asignatura_detalle.html', context)

# from django.shortcuts import render, redirect, get_object_or_404
# from django.views import View
# from django.contrib import messages
# from django.http import JsonResponse
# from Core.models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura
# from django.db.models import Count, Avg
# from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
# from django.utils import timezone
# from django.views.decorators.http import require_http_methods
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth import login, logout, authenticate
# from django.contrib.auth.hashers import make_password, check_password
# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from Core.servicios.repos import usuarios
# from Core.servicios.helpers import validadores, serializadores
# from Core.servicios.repos.cursos import get_estudiantes_por_curso

# @method_decorator(login_required, name='dispatch')
# class CursoView(View):
#     def get(self, request):
#         if not hasattr(request.user.usuario, 'estudiante'):
#             messages.error(request, 'No tienes permiso para acceder a esta página')
#             return redirect('home')
#         estudiantes = get_estudiantes_por_curso(request.user.usuario.estudiante.curso.id)
        
#         context = {
#             'estudiantes': estudiantes,
#             'curso': request.user.usuario.estudiante.curso
#         }
        
#         return render(request, 'student_panel.html', context)


