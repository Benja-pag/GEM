from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Usuario, Curso, EstudianteCurso, Calificacion
from django.db.models import Count, Avg
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('admin_panel')
        return super().get(request, *args, **kwargs)

class AdminPanelView(LoginRequiredMixin, View):
    template_name = 'admin_panel.html'
    
    def get(self, request):
        # Obtener estadísticas (solo para admin)
        if request.user.rol == 'admin':
            total_estudiantes = Usuario.objects.filter(rol='estudiante').count()
            total_profesores = Usuario.objects.filter(rol='profesor').count()
            total_cursos = Curso.objects.count()
            usuarios_recientes = Usuario.objects.exclude(rol='admin').order_by('-date_joined')
            cursos_activos = Curso.objects.filter(fecha_fin__gte=timezone.now())
            cursos_con_mas_estudiantes = Curso.objects.annotate(
                num_estudiantes=Count('estudiantecurso')
            ).order_by('-num_estudiantes')[:5]
            cursos_con_promedio = Curso.objects.annotate(
                promedio=Avg('calificacion__nota')
            ).order_by('-promedio')
        else:
            total_estudiantes = None
            total_profesores = None
            total_cursos = None
            usuarios_recientes = None
            cursos_activos = None
            cursos_con_mas_estudiantes = None
            cursos_con_promedio = None

        # Obtener datos según el rol del usuario
        if request.user.rol == 'profesor':
            mis_cursos = Curso.objects.filter(profesor=request.user)
            estudiantes_por_curso = {}
            for curso in mis_cursos:
                estudiantes_por_curso[curso] = EstudianteCurso.objects.filter(curso=curso)
        else:
            mis_cursos = None
            estudiantes_por_curso = None

        if request.user.rol == 'estudiante':
            cursos_inscritos = EstudianteCurso.objects.filter(estudiante=request.user)
            calificaciones = Calificacion.objects.filter(estudiante=request.user)
        else:
            cursos_inscritos = None
            calificaciones = None

        context = {
            'total_estudiantes': total_estudiantes,
            'total_profesores': total_profesores,
            'total_cursos': total_cursos,
            'usuarios_recientes': usuarios_recientes,
            'cursos_activos': cursos_activos,
            'cursos_con_mas_estudiantes': cursos_con_mas_estudiantes,
            'cursos_con_promedio': cursos_con_promedio,
            'mis_cursos': mis_cursos,
            'estudiantes_por_curso': estudiantes_por_curso,
            'cursos_inscritos': cursos_inscritos,
            'calificaciones': calificaciones,
            'is_admin': request.user.rol == 'admin'
        }
        
        return render(request, self.template_name, context)

class UserManagementView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Usuario
    template_name = 'user_management.html'
    context_object_name = 'usuarios'

    def test_func(self):
        return self.request.user.rol == 'admin'

    def get_queryset(self):
        return Usuario.objects.exclude(rol='admin').order_by('-date_joined')

@method_decorator(csrf_exempt, name='dispatch')
class UserCreateView(LoginRequiredMixin, View):
    def post(self, request):
        if not request.user.rol == 'admin':
            return JsonResponse({'success': False, 'error': 'No tienes permisos para realizar esta acción'})
        
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            rol = request.POST.get('rol')
            password = request.POST.get('password')

            if Usuario.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'error': 'El nombre de usuario ya existe'})

            if Usuario.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'error': 'El email ya está registrado'})

            user = Usuario.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                rol=rol
            )
            user.set_password(password)
            user.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class UserUpdateView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        if not request.user.rol == 'admin':
            return JsonResponse({'success': False, 'error': 'No tienes permisos para realizar esta acción'})
        
        try:
            user = get_object_or_404(Usuario, id=user_id)
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'rol': user.rol
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def post(self, request, user_id):
        if not request.user.rol == 'admin':
            return JsonResponse({'success': False, 'error': 'No tienes permisos para realizar esta acción'})
        
        try:
            user = get_object_or_404(Usuario, id=user_id)
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.rol = request.POST.get('rol')
            user.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class UserDeleteView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        if not request.user.rol == 'admin':
            return JsonResponse({'success': False, 'error': 'No tienes permisos para realizar esta acción'})
        
        try:
            user = get_object_or_404(Usuario, id=user_id)
            user.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

class AttendanceView(TemplateView):
    template_name = 'attendance.html'