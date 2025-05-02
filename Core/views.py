from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
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
            if request.user.rol == 'admin':
                return redirect('admin_panel')
            elif request.user.rol == 'profesor':
                return redirect('profesor_panel')
            elif request.user.rol == 'estudiante':
                return redirect('estudiante_panel')
        return super().get(request, *args, **kwargs)

class AdminPanelView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.rol == 'admin':
            # Estadísticas para admin
            total_estudiantes = Usuario.objects.filter(rol='estudiante').count()
            total_profesores = Usuario.objects.filter(rol='profesor').count()
            total_cursos = Curso.objects.count()
            cursos_activos = Curso.objects.filter(fecha_fin__gt=timezone.now().date()).count()
            promedio_general = Calificacion.objects.aggregate(Avg('nota'))['nota__avg'] or 0
            usuarios_recientes = Usuario.objects.exclude(rol='admin').order_by('-date_joined')[:5]
            cursos = Curso.objects.all().order_by('-fecha_inicio')
            profesores = Usuario.objects.filter(rol='profesor')
            
            context = {
                'total_estudiantes': total_estudiantes,
                'total_profesores': total_profesores,
                'total_cursos': total_cursos,
                'cursos_activos': cursos_activos,
                'promedio_general': promedio_general,
                'usuarios_recientes': usuarios_recientes,
                'cursos': cursos,
                'profesores': profesores,
                'user_rol': 'admin'
            }
            
        elif request.user.rol == 'profesor':
            # Contenido para profesor
            mis_cursos = Curso.objects.filter(profesor=request.user)
            context = {
                'cursos': mis_cursos,
                'user_rol': 'profesor'
            }
            
        else:  # estudiante
            # Contenido para estudiante
            cursos_inscritos = EstudianteCurso.objects.filter(estudiante=request.user).select_related('curso')
            mis_cursos = [inscripcion.curso for inscripcion in cursos_inscritos]
            mis_calificaciones = Calificacion.objects.filter(estudiante=request.user)
            context = {
                'cursos_inscritos': cursos_inscritos,
                'calificaciones': mis_calificaciones,
                'user_rol': 'estudiante'
            }
            
        return render(request, 'admin_panel.html', context)

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

class CursoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Curso
    template_name = 'curso_list.html'
    context_object_name = 'cursos'
    ordering = ['-fecha_inicio']

    def test_func(self):
        return self.request.user.rol == 'admin'

    def get_queryset(self):
        return Curso.objects.all().order_by('-fecha_inicio')

@method_decorator(csrf_exempt, name='dispatch')
class CursoCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.rol == 'admin'

    def post(self, request):
        try:
            nombre = request.POST.get('nombre')
            profesor_id = request.POST.get('profesor')
            descripcion = request.POST.get('descripcion')
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')

            profesor = Usuario.objects.get(id=profesor_id, rol='profesor')
            
            curso = Curso.objects.create(
                nombre=nombre,
                profesor=profesor,
                descripcion=descripcion,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

class CursoUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.rol == 'admin'

    def get(self, request, curso_id):
        try:
            curso = Curso.objects.get(id=curso_id)
            return JsonResponse({
                'success': True,
                'curso': {
                    'id': curso.id,
                    'nombre': curso.nombre,
                    'profesor_id': curso.profesor.id,
                    'descripcion': curso.descripcion,
                    'fecha_inicio': curso.fecha_inicio.strftime('%Y-%m-%d'),
                    'fecha_fin': curso.fecha_fin.strftime('%Y-%m-%d')
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def post(self, request, curso_id):
        try:
            curso = Curso.objects.get(id=curso_id)
            
            curso.nombre = request.POST.get('nombre')
            profesor_id = request.POST.get('profesor')
            curso.profesor = Usuario.objects.get(id=profesor_id, rol='profesor')
            curso.descripcion = request.POST.get('descripcion')
            curso.fecha_inicio = request.POST.get('fecha_inicio')
            curso.fecha_fin = request.POST.get('fecha_fin')
            
            curso.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

class CursoDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.rol == 'admin'

    def post(self, request, curso_id):
        try:
            curso = Curso.objects.get(id=curso_id)
            curso.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

class CursoDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Curso
    template_name = 'curso_detail.html'
    context_object_name = 'curso'

    def test_func(self):
        return self.request.user.rol == 'admin'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estudiantes'] = EstudianteCurso.objects.filter(curso=self.object)
        calificaciones = Calificacion.objects.filter(curso=self.object)
        context['calificaciones'] = {cal.estudiante.id: cal for cal in calificaciones}
        context['now'] = timezone.now()
        return context

class ProfesorPanelView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.rol != 'profesor':
            return redirect('home')
        
        # Obtener cursos del profesor
        cursos = Curso.objects.filter(profesor=request.user)
        
        context = {
            'cursos': cursos,
        }
        
        return render(request, 'profesor_panel.html', context)

class EstudiantePanelView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.rol != 'estudiante':
            return redirect('home')
        
        # Obtener cursos del estudiante
        cursos_inscritos = EstudianteCurso.objects.filter(estudiante=request.user)
        
        # Obtener calificaciones del estudiante
        calificaciones = Calificacion.objects.filter(estudiante=request.user)
        
        context = {
            'cursos_inscritos': cursos_inscritos,
            'calificaciones': calificaciones,
        }
        
        return render(request, 'estudiante_panel.html', context)
