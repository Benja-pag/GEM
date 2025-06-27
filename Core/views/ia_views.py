"""
Vistas para manejar las interacciones con la IA.
"""

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from Core.servicios.helpers.ia_service import IAService
from Core.servicios.helpers.ia_config import TEMPLATES
from ..models.cursos import Curso
from ..models.usuarios import Usuario

@login_required
@require_http_methods(["POST"])
def generar_reporte(request):
    try:
        data = json.loads(request.body)
        tipo = data.get('tipo')
        curso_id = data.get('curso_id')
        contexto = data.get('contexto', {})
        
        if not request.user.has_perm('Core.puede_usar_ia'):
            raise PermissionDenied("No tienes permisos para usar las herramientas de IA")
        
        ia_service = IAService()
        resultado = ia_service.generar_reporte(tipo, curso_id, contexto)
        
        return JsonResponse(resultado)
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def generar_sugerencias(request):
    try:
        data = json.loads(request.body)
        tipo = data.get('tipo')
        curso_id = data.get('curso_id')
        contexto = data.get('contexto', {})
        
        if not request.user.has_perm('Core.puede_usar_ia'):
            raise PermissionDenied("No tienes permisos para usar las herramientas de IA")
        
        ia_service = IAService()
        resultado = ia_service.generar_sugerencias(tipo, curso_id, contexto)
        
        return JsonResponse(resultado)
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def generar_comunicado(request):
    try:
        data = json.loads(request.body)
        tipo = data.get('tipo')
        curso_id = data.get('curso_id')
        contexto = data.get('contexto', {})
        
        if not request.user.has_perm('Core.puede_usar_ia'):
            raise PermissionDenied("No tienes permisos para usar las herramientas de IA")
        
        ia_service = IAService()
        resultado = ia_service.generar_comunicado(tipo, curso_id, contexto)
        
        return JsonResponse(resultado)
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def chat_ia(request):
    try:
        data = json.loads(request.body)
        mensaje = data.get('mensaje')
        curso_id = data.get('curso_id')
        contexto = data.get('contexto', {})
        
        if not request.user.has_perm('Core.puede_usar_ia'):
            raise PermissionDenied("No tienes permisos para usar las herramientas de IA")
        
        ia_service = IAService()
        resultado = ia_service.procesar_mensaje_chat(mensaje, curso_id, contexto)
        
        return JsonResponse(resultado)
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def exportar_reporte(request):
    try:
        data = json.loads(request.body)
        formato = data.get('formato')
        reporte_id = data.get('reporte_id')
        
        if not request.user.has_perm('Core.puede_usar_ia'):
            raise PermissionDenied("No tienes permisos para usar las herramientas de IA")
        
        ia_service = IAService()
        archivo = ia_service.exportar_reporte(reporte_id, formato)
        
        return JsonResponse({
            'success': True,
            'archivo_url': archivo
        })
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def aplicar_sugerencias(request):
    try:
        data = json.loads(request.body)
        sugerencias_id = data.get('sugerencias_id')
        curso_id = data.get('curso_id')
        
        if not request.user.has_perm('Core.puede_usar_ia'):
            raise PermissionDenied("No tienes permisos para usar las herramientas de IA")
        
        ia_service = IAService()
        resultado = ia_service.aplicar_sugerencias(sugerencias_id, curso_id)
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Sugerencias aplicadas correctamente'
        })
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def enviar_comunicado(request):
    try:
        data = json.loads(request.body)
        comunicado_id = data.get('comunicado_id')
        destinatarios = data.get('destinatarios', [])
        
        if not request.user.has_perm('Core.puede_usar_ia'):
            raise PermissionDenied("No tienes permisos para usar las herramientas de IA")
        
        ia_service = IAService()
        resultado = ia_service.enviar_comunicado(comunicado_id, destinatarios)
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Comunicado enviado correctamente'
        })
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 