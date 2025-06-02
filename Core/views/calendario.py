from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from Core.models.calendarios import CalendarioClase, CalendarioColegio
from datetime import datetime
import json

class CalendarioView(LoginRequiredMixin, TemplateView):
    template_name = 'calendar.html'

    def dispatch(self, request, *args, **kwargs):
        # Aquí podrías agregar permisos extras si quieres
        if not hasattr(request.user.usuario, 'estudiante'):
            messages.error(request, 'No tienes permiso para acceder al calendario')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CalendarioEventosView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Obtener eventos de clase
        eventos_clase = CalendarioClase.objects.all().values(
            'id', 'nombre_actividad', 'descripcion', 'fecha', 'hora'
        )
        
        # Obtener eventos del colegio
        eventos_colegio = CalendarioColegio.objects.all().values(
            'id', 'nombre_actividad', 'descripcion', 'fecha', 'hora'
        )
        
        # Formatear eventos para FullCalendar
        eventos = []
        for evento in eventos_clase:
            eventos.append({
                'id': f"clase_{evento['id']}",
                'title': evento['nombre_actividad'],
                'description': evento['descripcion'],
                'start': f"{evento['fecha']}T{evento['hora']}",
                'className': 'evento-clase'
            })
            
        for evento in eventos_colegio:
            eventos.append({
                'id': f"colegio_{evento['id']}",
                'title': evento['nombre_actividad'],
                'description': evento['descripcion'],
                'start': f"{evento['fecha']}T{evento['hora']}",
                'className': 'evento-colegio'
            })
            
        return JsonResponse(eventos, safe=False)

@method_decorator(require_http_methods(["POST"]), name='dispatch')
class CalendarioGuardarEventoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body) if request.body else request.POST
            
            evento_id = data.get('eventId')
            tipo_evento = data.get('eventType', 'clase')
            
            evento_data = {
                'nombre_actividad': data['title'],
                'descripcion': data.get('description', ''),
                'fecha': datetime.strptime(data['date'], '%Y-%m-%d').date(),
                'hora': data['time']
            }
            
            if evento_id:
                # Actualizar evento existente
                id_num = evento_id.split('_')[1]
                if tipo_evento == 'clase':
                    evento = CalendarioClase.objects.get(id=id_num)
                else:
                    evento = CalendarioColegio.objects.get(id=id_num)
                
                for key, value in evento_data.items():
                    setattr(evento, key, value)
                evento.save()
            else:
                # Crear nuevo evento
                if tipo_evento == 'clase':
                    CalendarioClase.objects.create(**evento_data)
                else:
                    CalendarioColegio.objects.create(**evento_data)
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(require_http_methods(["POST"]), name='dispatch')
class CalendarioEliminarEventoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            evento_id = request.POST.get('eventId')
            tipo_evento, id_num = evento_id.split('_')
            
            if tipo_evento == 'clase':
                CalendarioClase.objects.filter(id=id_num).delete()
            else:
                CalendarioColegio.objects.filter(id=id_num).delete()
                
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})