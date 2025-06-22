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


class HomeView(TemplateView):
    template_name = 'base/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                usuario = Usuario.objects.get(auth_user=self.request.user)
                context['usuario'] = usuario
            except Usuario.DoesNotExist:
                messages.error(self.request, 'Error: Usuario no encontrado')
        return context

class SurveysView(TemplateView):
    template_name = 'surveys.html'

class TasksView(TemplateView):
    template_name = 'tasks.html'

class TestsView(TemplateView):
    template_name = 'tests.html'