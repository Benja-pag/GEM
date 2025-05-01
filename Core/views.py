from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import JsonResponse
from .forms import UsuarioAdminForm
from .models import Usuario, Asignatura
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def is_administrador(user):
    return user.is_authenticated and user.tipo_usuario == 'administrador'

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            if user.tipo_usuario == 'administrador':
                return redirect('admin_panel')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Email o contraseña incorrectos.')
    
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

@login_required
@user_passes_test(is_administrador)
def admin_panel(request):
    usuarios = Usuario.objects.all()
    asignaturas = Asignatura.objects.filter(activa=True)
    print("=== ASIGNATURAS EN VISTA ===")
    print("Total asignaturas:", asignaturas.count())
    for asignatura in asignaturas:
        print(f"- {asignatura.nombre}")
    form = UsuarioAdminForm()
    context = {
        'usuarios': usuarios,
        'asignaturas': asignaturas,
        'form': form
    }
    return render(request, 'admin_panel.html', context)

@login_required
@user_passes_test(is_administrador)
def crear_usuario(request):
    if request.method == 'POST':
        print("=== INICIO DE CREAR USUARIO ===")
        print("Datos recibidos:", request.POST)
        
        form = UsuarioAdminForm(request.POST)
        print("Formulario creado")
        print("Es válido?", form.is_valid())
        
        if form.is_valid():
            try:
                # Obtener los datos del formulario
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                rut = form.cleaned_data.get('rut')
                password = form.cleaned_data.get('password1')
                
                print(f"Intentando crear usuario: {first_name} {last_name}")
                
                # Crear el usuario
                user = form.save()
                print(f"Usuario creado con ID: {user.id}")
                
                # Enviar correo con las credenciales
                context = {
                    'nombre': f"{first_name} {last_name}",
                    'email': user.email,
                    'rut': rut,
                    'password': password
                }
                
                message = render_to_string('credenciales_email.txt', context)
                print("Mensaje de correo generado:", message)
                
                try:
                    print("Intentando enviar correo a:", user.email)
                    send_mail(
                        'Bienvenido/a al Sistema GEM - Tus Credenciales',
                        message,
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False,
                    )
                    print("Correo enviado exitosamente")
                    
                    # Enviar una copia al administrador
                    admin_message = f"Se ha creado un nuevo usuario:\n\nNombre: {first_name} {last_name}\nEmail: {user.email}\nRUT: {rut}\nTipo: {user.get_tipo_usuario_display()}"
                    send_mail(
                        'Nuevo usuario creado en GEM',
                        admin_message,
                        settings.EMAIL_HOST_USER,
                        [settings.EMAIL_HOST_USER],
                        fail_silently=False,
                    )
                    print("Copia enviada al administrador")
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Usuario creado exitosamente. Las credenciales han sido enviadas al correo electrónico.'
                    })
                except Exception as e:
                    print(f"Error al enviar correo: {str(e)}")
                    return JsonResponse({
                        'success': False,
                        'message': f'Usuario creado pero hubo un error al enviar el correo: {str(e)}'
                    })
            except Exception as e:
                print(f"Error al crear usuario: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': f'Error al crear el usuario: {str(e)}'
                })
        else:
            print("Errores del formulario:", form.errors)
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })

@login_required
@user_passes_test(is_administrador)
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if request.method == 'POST':
        form = UsuarioAdminForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
@user_passes_test(is_administrador)
def cambiar_estado_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    usuario.is_active = not usuario.is_active
    usuario.save()
    return JsonResponse({
        'success': True,
        'is_active': usuario.is_active
    })
