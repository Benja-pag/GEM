from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from Core.models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura
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
class UserManagementView(View):
    def get(self, request):
        if not request.user.is_admin:
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        
        users = Usuario.objects.all().order_by('-fecha_creacion')
        context = {
            'users': users,
            'total_estudiantes': Usuario.objects.filter(estudiante__isnull=False).count(),
            'total_profesores': Usuario.objects.filter(docente__isnull=False).count(),
            'total_clases': Clase.objects.count(),
            'clases': Clase.objects.all().order_by('nombre')[:10],
            'now': timezone.now(),
        }
        return render(request, 'admin_panel.html', context)

@method_decorator(login_required, name='dispatch')
class UserCreateView(View):
    def get(self, request):
        if not request.user.administrativo:
            messages.error(request, 'No tienes permiso para acceder a esta página.')
            return redirect('home')
        return render(request, 'user_create.html')

    def post(self, request):
        if not request.user.administrativo:
            return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción.'})

        try:
            success, errores = validadores.validar_data_crear_usuario(request.POST)
            if success:
                # Crear usuario
                usuarios.crear_usuario(request.POST, request.POST.get('tipo_usuario'))
                return JsonResponse({'success': True, 'message': 'Usuario creado exitosamente.'})
            else:
                return JsonResponse({'success': False, 'errors': errores})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator([login_required, csrf_exempt], name='dispatch')
class UserDetailView(View):
    def get(self, request, user_id):
        try:
            usuario = get_object_or_404(Usuario, auth_user_id=user_id)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'data': serializadores.usuario_a_dict(usuario)
                })
            return redirect('admin_panel')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, str(e))
            return redirect('admin_panel')

@method_decorator([login_required, csrf_exempt], name='dispatch')
class UserUpdateView(View):
    def get(self, request, user_id):
        try:
            usuario = get_object_or_404(Usuario, auth_user_id=user_id)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'data': serializadores.usuario_a_dict(usuario)
                })
            return redirect('admin_panel')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, str(e))
            return redirect('admin_panel')

    def post(self, request, user_id):
        try:
            usuario = get_object_or_404(Usuario, auth_user_id=user_id)
            usuarios.actualizar_usuario(usuario, request.POST)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            messages.success(request, 'Usuario actualizado exitosamente')
            return redirect('admin_panel')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, str(e))
            return redirect('admin_panel')

@method_decorator([login_required, csrf_exempt], name='dispatch')
class UserDeleteView(View):
    def post(self, request, user_id):
        try:
            with transaction.atomic():
                usuario = get_object_or_404(Usuario, auth_user_id=user_id)
                
                # Verificar si es un administrador máximo
                if hasattr(usuario, 'administrativo') and usuario.administrativo.rol == 'ADMINISTRADOR':
                    # Contar cuántos administradores máximos hay
                    total_admins = Administrativo.objects.filter(rol='ADMINISTRADOR').count()
                    
                    # Si es el único administrador máximo, no permitir eliminarlo
                    if total_admins <= 1:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': False, 
                                'error': 'No se puede eliminar el último administrador máximo. Debe haber al menos un administrador máximo en el sistema.'
                            })
                        messages.error(request, 'No se puede eliminar el último administrador máximo. Debe haber al menos un administrador máximo en el sistema.')
                        return redirect('admin_panel')
                
                # Guardar referencia al AuthUser antes de eliminar el Usuario
                auth_user = usuario.auth_user
                
                # Eliminar el usuario (esto eliminará automáticamente las relaciones con on_delete=CASCADE)
                usuario.delete()
                
                # Eliminar explícitamente el AuthUser
                auth_user.delete()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                messages.success(request, 'Usuario eliminado exitosamente')
                return redirect('admin_panel')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, str(e))
            return redirect('admin_panel')

@method_decorator(csrf_exempt, name='dispatch')
class UserDataView(View):
    def get(self, request, user_id):
        try:
            # Verificar que el usuario está autenticado
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'error': 'Usuario no autenticado'})
            
            # Verificar que el usuario tiene permisos
            if not (hasattr(request.user, 'is_admin') and request.user.is_admin):
                return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'})
            
            usuario = get_object_or_404(Usuario, auth_user_id=user_id)
            return JsonResponse({
                'success': True,
                'data': serializadores.usuario_a_dict(usuario)
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def post(self, request, user_id):
        try:
            # Verificar que el usuario está autenticado
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'error': 'Usuario no autenticado'})
            
            # Verificar que el usuario tiene permisos
            if not (hasattr(request.user, 'is_admin') and request.user.is_admin):
                return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'})

            usuario = get_object_or_404(Usuario, auth_user_id=user_id)
            
            # Verificar si el usuario es administrador máximo
            if hasattr(usuario, 'administrativo') and usuario.administrativo.rol == 'ADMINISTRADOR_MAXIMO':
                return JsonResponse({'success': False, 'error': 'No se puede modificar un administrador máximo'})
            
            # Actualizar el usuario usando el servicio
            usuario = usuarios.actualizar_usuario(usuario, request.POST)
            
            return JsonResponse({
                'success': True,
                'data': serializadores.usuario_a_dict(usuario)
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator([login_required, csrf_exempt], name='dispatch')
class CleanupAuthUsersView(View):
    def post(self, request):
        if not request.user.is_admin:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'No tienes permiso para realizar esta acción'
                })
            messages.error(request, 'No tienes permiso para realizar esta acción')
            return redirect('admin_panel')
        
        try:
            cantidad = usuarios.limpiar_authusers_huerfanos()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Se eliminaron {cantidad} registros huérfanos de AuthUser'
                })
            messages.success(request, f'Se eliminaron {cantidad} registros huérfanos de AuthUser')
            return redirect('admin_panel')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, str(e))
            return redirect('admin_panel')

@method_decorator([login_required, csrf_exempt], name='dispatch')
class ToggleUserStatusView(View):
    def post(self, request, user_id):
        try:
            with transaction.atomic():
                # Verificar permisos
                if not request.user.is_admin:
                    return JsonResponse({
                        'success': False,
                        'error': 'No tienes permiso para realizar esta acción'
                    })
                
                # Obtener el usuario
                usuario = get_object_or_404(Usuario, auth_user_id=user_id)
                
                # No permitir desactivar administradores máximos
                if hasattr(usuario, 'administrativo') and usuario.administrativo.rol == 'ADMINISTRADOR':
                    total_admins = Administrativo.objects.filter(rol='ADMINISTRADOR', usuario__activador=True).count()
                    if total_admins <= 1:
                        return JsonResponse({
                            'success': False,
                            'error': 'No se puede desactivar el último administrador máximo activo'
                        })
                
                # Cambiar estado en Usuario
                usuario.activador = not usuario.activador
                usuario.save()
                
                # Cambiar estado en AuthUser
                auth_user = usuario.auth_user
                auth_user.is_active = usuario.activador
                auth_user.save()
                
                return JsonResponse({
                    'success': True,
                    'is_active': usuario.activador
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
        
