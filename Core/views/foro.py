from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from Core.models import Foro, MensajeForo, Usuario

@method_decorator(login_required, name='dispatch')
class ForoGeneralView(View):
    """
    Vista para mostrar la lista de todos los temas del foro general.
    """
    template_name = 'foro/foro_general.html'

    def get(self, request):
        temas = Foro.objects.all().order_by('-fecha', '-hora')
        context = {
            'temas': temas
        }
        return render(request, self.template_name, context)

@method_decorator(login_required, name='dispatch')
class TemaForoView(View):
    """
    Vista para mostrar un tema específico y sus mensajes.
    También maneja la creación de nuevas respuestas.
    """
    template_name = 'foro/tema_detalle.html'

    def get(self, request, tema_id):
        tema = get_object_or_404(Foro, id=tema_id)
        mensajes = MensajeForo.objects.filter(foro=tema).order_by('fecha')
        context = {
            'tema': tema,
            'mensajes': mensajes
        }
        return render(request, self.template_name, context)

    def post(self, request, tema_id):
        tema = get_object_or_404(Foro, id=tema_id)
        contenido = request.POST.get('contenido')
        
        if not contenido:
            messages.error(request, 'No puedes enviar un mensaje vacío.')
            return redirect('ver_tema_foro', tema_id=tema.id)

        # Asumo que el usuario autenticado está en request.user y es una instancia de AuthUser
        # y que tu modelo Usuario tiene una relación con AuthUser.
        try:
            autor = Usuario.objects.get(auth_user=request.user)
        except Usuario.DoesNotExist:
            messages.error(request, 'Tu cuenta de usuario no está configurada correctamente.')
            return redirect('ver_tema_foro', tema_id=tema.id)

        MensajeForo.objects.create(
            foro=tema,
            autor=autor,
            contenido=contenido
        )
        messages.success(request, 'Tu respuesta ha sido publicada.')
        return redirect('ver_tema_foro', tema_id=tema.id)

@method_decorator(login_required, name='dispatch')
class CrearTemaForoView(View):
    """
    Vista para manejar la creación de un nuevo tema en el foro.
    """
    template_name = 'foro/crear_tema.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')

        if not titulo or not contenido:
            messages.error(request, 'El título y el contenido son obligatorios.')
            return render(request, self.template_name)

        try:
            autor = Usuario.objects.get(auth_user=request.user)
        except Usuario.DoesNotExist:
            messages.error(request, 'Tu cuenta de usuario no está configurada correctamente.')
            return render(request, self.template_name)

        nuevo_tema = Foro.objects.create(
            titulo=titulo,
            asunto=titulo, # Usando título como asunto por simplicidad
            contenido=contenido,
            autor=autor
        )
        messages.success(request, 'El nuevo tema ha sido creado exitosamente.')
        return redirect('ver_tema_foro', tema_id=nuevo_tema.id) 