from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from Core.models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, Nota, AuthUser, Asignatura
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

@method_decorator(csrf_exempt, name='dispatch')
class UserDetailView(View):
    def get(self, request, user_id):
        try:
            user = usuarios.obtener_usuario_por_id(user_id)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'user': serializadores.usuario_a_dict(user)
                })
            return redirect('admin_panel')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, str(e))
            return redirect('admin_panel')

@method_decorator(csrf_exempt, name='dispatch')
class UserUpdateView(View):
    def get(self, request, user_id):
        try:
            user = get_object_or_404(Usuario, id=user_id)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'user': serializadores.usuario_a_dict(user)
                })
            return redirect('admin_panel')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, str(e))
            return redirect('admin_panel')

    def post(self, request, user_id):
        try:
            user = get_object_or_404(Usuario, id=user_id)
            usuarios.actualizar_usuario(user, request.POST)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            messages.success(request, 'Usuario actualizado exitosamente')
            return redirect('admin_panel')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, str(e))
            return redirect('admin_panel')

@method_decorator(csrf_exempt, name='dispatch')
class UserDeleteView(View):
    def post(self, request, user_id):
        try:
            usuario = get_object_or_404(Usuario, id=user_id)
            
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
            
            # Si no es el último administrador máximo o no es administrador, proceder con la eliminación
            usuario.delete()
            
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
            # Separar el RUT y el dígito verificador
            rut_parts = user_id.split('-')
            if len(rut_parts) != 2:
                return JsonResponse({'success': False, 'error': 'Formato de RUT inválido'})
            
            rut = rut_parts[0]
            div = rut_parts[1]
            
            usuario = get_object_or_404(Usuario, rut=rut, div=div)
            data = {
                'success': True,
                'data': {
                    'nombre': usuario.nombre,
                    'apellido_paterno': usuario.apellido_paterno,
                    'apellido_materno': usuario.apellido_materno,
                    'rut': usuario.rut,
                    'div': usuario.div,
                    'correo': usuario.correo,
                    'telefono': usuario.telefono,
                    'direccion': usuario.direccion,
                    'fecha_nacimiento': usuario.fecha_nacimiento.strftime('%Y-%m-%d') if usuario.fecha_nacimiento else None,
                    'tipo_usuario': 'estudiante' if hasattr(usuario, 'estudiante') else 'docente' if hasattr(usuario, 'docente') else 'administrativo',
                }
            }
            
            # Agregar datos específicos según el tipo de usuario
            if hasattr(usuario, 'estudiante'):
                data['data']['contacto_emergencia'] = usuario.estudiante.contacto_emergencia
            elif hasattr(usuario, 'administrativo'):
                data['data']['rol_administrativo'] = usuario.administrativo.rol
            
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def post(self, request, user_id):
        try:
            # Verificar que el usuario que hace la petición es docente o administrador
            if not (hasattr(request.user.usuario, 'docente') or hasattr(request.user.usuario, 'administrativo')):
                return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'})

            # Separar el RUT y el dígito verificador
            rut_parts = user_id.split('-')
            if len(rut_parts) != 2:
                return JsonResponse({'success': False, 'error': 'Formato de RUT inválido'})
            
            rut = rut_parts[0]
            div = rut_parts[1]
            
            usuario = get_object_or_404(Usuario, rut=rut, div=div)
            
            # Verificar si el usuario es administrador máximo
            if hasattr(usuario, 'administrativo') and usuario.administrativo.rol == 'ADMINISTRADOR_MAXIMO':
                return JsonResponse({'success': False, 'error': 'No se puede modificar un administrador máximo'})
            
            # Actualizar datos básicos
            usuario.nombre = request.POST.get('nombre')
            usuario.apellido_paterno = request.POST.get('apellido_paterno')
            usuario.apellido_materno = request.POST.get('apellido_materno')
            usuario.rut = request.POST.get('rut')
            usuario.div = request.POST.get('div')
            usuario.correo = request.POST.get('correo')
            usuario.telefono = request.POST.get('telefono')
            usuario.direccion = request.POST.get('direccion')
            usuario.fecha_nacimiento = request.POST.get('fecha_nacimiento')
            usuario.save()
            
            # Actualizar datos de AuthUser
            auth_user = usuario.auth_user
            auth_user.rut = request.POST.get('rut')
            auth_user.div = request.POST.get('div')
            auth_user.correo = request.POST.get('correo')
            auth_user.telefono = request.POST.get('telefono')
            auth_user.direccion = request.POST.get('direccion')
            auth_user.fecha_nacimiento = request.POST.get('fecha_nacimiento')
            auth_user.save()
            
            # Manejar cambio de tipo de usuario
            nuevo_tipo = request.POST.get('tipo_usuario')
            tipo_actual = 'estudiante' if hasattr(usuario, 'estudiante') else 'docente' if hasattr(usuario, 'docente') else 'administrativo'
            
            # Solo permitir cambio de tipo si el usuario que hace la petición es administrador
            if nuevo_tipo != tipo_actual and hasattr(request.user.usuario, 'administrativo'):
                # Eliminar el tipo actual
                if hasattr(usuario, 'estudiante'):
                    usuario.estudiante.delete()
                elif hasattr(usuario, 'docente'):
                    usuario.docente.delete()
                elif hasattr(usuario, 'administrativo'):
                    usuario.administrativo.delete()
                
                # Crear el nuevo tipo
                if nuevo_tipo == 'estudiante':
                    Estudiante.objects.create(
                        usuario=usuario,
                        contacto_emergencia=request.POST.get('contacto_emergencia')
                    )
                elif nuevo_tipo == 'docente':
                    Docente.objects.create(usuario=usuario)
                elif nuevo_tipo == 'administrativo':
                    Administrativo.objects.create(
                        usuario=usuario,
                        rol='ADMINISTRADOR'  # Siempre se crea como administrador normal
                    )
            
            # Actualizar datos específicos según el tipo de usuario
            if nuevo_tipo == 'estudiante' and hasattr(usuario, 'estudiante'):
                usuario.estudiante.contacto_emergencia = request.POST.get('contacto_emergencia')
                usuario.estudiante.save()
            elif nuevo_tipo == 'administrativo' and hasattr(usuario, 'administrativo'):
                usuario.administrativo.rol = 'ADMINISTRADOR'  # Siempre se mantiene como administrador normal
                usuario.administrativo.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
