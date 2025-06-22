from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from Core.models import Usuario, Administrativo, Docente, Estudiante, Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, AuthUser, Asignatura, AsignaturaImpartida, Curso, ProfesorJefe, Especialidad
from django.db.models import Count, Avg
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from Core.servicios.repos import usuarios
from Core.servicios.helpers import validadores, serializadores
from Core.servicios.repos.usuarios import crear_usuario, actualizar_usuario
from Core.servicios.repos.cursos import get_curso, get_estudiantes_por_curso
from django.http import JsonResponse

@method_decorator(login_required, name='dispatch')
class AdminPanelView(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            return redirect('login')
        try:
            # Obtener estadísticas
            total_estudiantes = Estudiante.objects.count()
            total_profesores = Docente.objects.count()
            total_asignaturas_impartidas = AsignaturaImpartida.objects.count()
            total_administradores = Administrativo.objects.count()
            total_clases = Clase.objects.count()
            total_asignaturas = Asignatura.objects.count()
            
            # Obtener todos los docentes con sus relaciones
            docentes = Docente.objects.select_related(
                'usuario',
                'especialidad'
            ).prefetch_related(
                'jefaturas'
            ).all()
            
            # Debug: imprimir información de los docentes
            print(f"Total de docentes encontrados: {len(docentes)}")
            for docente in docentes:
                print(f"Docente: {docente.usuario.nombre} {docente.usuario.apellido_paterno}")
                print(f"- ID: {docente.usuario.auth_user_id}")
                print(f"- Es profesor jefe: {docente.es_profesor_jefe}")
                print(f"- Tiene jefatura: {docente.jefaturas.exists()}")
            
            # Obtener todos los estudiantes
            estudiantes_sin_curso = Estudiante.objects.all().select_related('usuario', 'curso')
            
            # Obtener todos los usuarios ordenados por fecha de creación
            usuarios = Usuario.objects.all().order_by('-fecha_creacion')
            
            # Obtener todas las asignaturas con sus relaciones
            asignaturas = AsignaturaImpartida.objects.select_related(
                'asignatura',
                'docente__usuario'
            ).prefetch_related('clases').all()
            
            # Obtener cursos con sus profesores jefe
            cursos = Curso.objects.select_related('jefatura_actual__docente__usuario').all()
            
            # Obtener todas las especialidades
            especialidades = Especialidad.objects.all()
            
            context = {
                'total_estudiantes': total_estudiantes,
                'total_profesores': total_profesores,
                'total_asignaturas_impartidas': total_asignaturas_impartidas,
                'total_administradores': total_administradores,
                'total_clases': total_clases,
                'total_asignaturas': total_asignaturas,
                'docentes': docentes,
                'estudiantes_sin_curso': estudiantes_sin_curso,
                'usuarios': usuarios,
                'asignaturas': asignaturas,
                'cursos': cursos,
                'especialidades': especialidades,
            }
            return render(request, 'admin_panel.html', context)
        except Exception as e:
            messages.error(request, f'Error al cargar el panel de administrador: {str(e)}')
            return redirect('home')

    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, 'No tienes permiso para realizar esta acción')
            return redirect('login')

        try:
            action = request.POST.get('action')
            print("ok")
            if action == 'crear_curso':
                try:
                    # Validar datos
                    nivel = request.POST.get('nivel')
                    letra = request.POST.get('letra', '').upper()
                    profesor_jefe_id = request.POST.get('profesor_jefe_id')
                    
                    errores = []
                    if not nivel or not nivel.isdigit() or int(nivel) < 1 or int(nivel) > 4:
                        errores.append('El nivel debe estar entre 1 y 4')
                    
                    if not letra or letra not in ['A', 'B', 'C']:
                        errores.append('La letra debe ser A o B')
                    
                    if not profesor_jefe_id:
                        errores.append('Debe seleccionar un profesor jefe')
                    
                    # Verificar si ya existe un curso con el mismo nivel y letra
                    if Curso.objects.filter(nivel=nivel, letra=letra).exists():
                        errores.append(f'Ya existe un curso {nivel}°{letra}')
                    
                    # Verificar si el profesor ya es jefe de otro curso
                    if profesor_jefe_id:
                        docente = get_object_or_404(Docente, usuario__auth_user_id=profesor_jefe_id)
                        if docente.jefaturas.filter(curso__isnull=False).exists():
                            errores.append('El profesor seleccionado ya es jefe de otro curso')
                    
                    if errores:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': False,
                                'errors': errores
                            })
                        for error in errores:
                            messages.error(request, error)
                        return redirect('admin_panel')
                    
                    with transaction.atomic():
                        # Crear el curso
                        curso = Curso.objects.create(
                            nivel=nivel,
                            letra=letra
                        )
                        
                        # Actualizar el docente y crear la relación de profesor jefe
                        docente = get_object_or_404(Docente, usuario__auth_user_id=profesor_jefe_id)
                        docente.es_profesor_jefe = True
                        docente.save()
                        
                        ProfesorJefe.objects.create(
                            docente=docente,
                            curso=curso
                        )
                        
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': True,
                                'message': f'Curso {curso.nivel}°{curso.letra} creado exitosamente'
                            })
                        
                        messages.success(request, f'Curso {curso.nivel}°{curso.letra} creado exitosamente')
                        return redirect('admin_panel')
                        
                except Exception as e:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': [str(e)]
                        })
                    messages.error(request, f'Error al crear curso: {str(e)}')
                    return redirect('admin_panel')
            
            elif action == 'crear_estudiante':
                data = {
                    'nombre': request.POST.get('nombre'),
                    'apellido_paterno': request.POST.get('apellido_paterno'),
                    'apellido_materno': request.POST.get('apellido_materno'),
                    'rut': request.POST.get('rut'),
                    'div': request.POST.get('div'),
                    'correo': request.POST.get('correo'),
                    'telefono': request.POST.get('telefono'),
                    'direccion': request.POST.get('direccion'),
                    'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                    'password': request.POST.get('password'),
                    'contacto_emergencia': request.POST.get('contacto_emergencia'),
                    'curso': request.POST.get('curso')
                }
                
                # Validar datos
                es_valido, errores = validadores.validar_data_crear_usuario(data, tipo_usuario='ESTUDIANTE')
                if not es_valido:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': errores
                        })
                    for error in errores:
                        messages.error(request, error)
                    return redirect('admin_panel')
                
                try:
                    usuario = crear_usuario(data, 'ESTUDIANTE')
                    messages.success(request, f'Estudiante {usuario.nombre} {usuario.apellido_paterno} creado exitosamente')
                except Exception as e:
                    messages.error(request, f'Error al crear estudiante: {str(e)}')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                return redirect('admin_panel')
                    
            elif action == 'crear_docente':
                data = {
                    'nombre': request.POST.get('nombre'),
                    'apellido_paterno': request.POST.get('apellido_paterno'),
                    'apellido_materno': request.POST.get('apellido_materno'),
                    'rut': request.POST.get('rut'),
                    'div': request.POST.get('div'),
                    'correo': request.POST.get('correo'),
                    'telefono': request.POST.get('telefono'),
                    'direccion': request.POST.get('direccion'),
                    'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                    'password': request.POST.get('password'),
                    'confirm_password': request.POST.get('confirm_password'),
                    'especialidad': request.POST.get('especialidad'),
                    'es_profesor_jefe': request.POST.get('es_profesor_jefe') == 'true'
                }
                
                # Validar datos
                es_valido, errores = validadores.validar_data_crear_usuario(data, tipo_usuario='DOCENTE')
                if not es_valido:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': {'__all__': errores}
                        })
                    for error in errores:
                        messages.error(request, error)
                    return redirect('admin_panel')
                
                try:
                    # Crear usuario base y docente
                    usuario = crear_usuario(data, 'DOCENTE')
                    messages.success(request, f'Docente {usuario.nombre} {usuario.apellido_paterno} creado exitosamente')
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    return redirect('admin_panel')
                    
                except Exception as e:
                    messages.error(request, f'Error al crear docente: {str(e)}')
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'errors': {'__all__': [str(e)]}})
                    return redirect('admin_panel')
                    
            elif action == 'crear_administrador':
                data = {
                    'nombre': request.POST.get('nombre'),
                    'apellido_paterno': request.POST.get('apellido_paterno'),
                    'apellido_materno': request.POST.get('apellido_materno'),
                    'rut': request.POST.get('rut'),
                    'div': request.POST.get('div'),
                    'correo': request.POST.get('correo'),
                    'telefono': request.POST.get('telefono'),
                    'direccion': request.POST.get('direccion'),
                    'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                    'password': request.POST.get('password'),
                    'confirm_password': request.POST.get('confirm_password'),
                    'tipo_usuario': 'ADMINISTRATIVO',
                    'rol': request.POST.get('rol', 'ADMINISTRATIVO')
                }
                
                # Validar datos
                es_valido, errores = validadores.validar_data_crear_usuario(data, tipo_usuario='ADMINISTRATIVO')
                if not es_valido:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': {'__all__': errores}
                        })
                    for error in errores:
                        messages.error(request, error)
                    return redirect('admin_panel')
                
                try:
                    # Crear usuario base y administrativo
                    usuario = crear_usuario(data, 'ADMINISTRATIVO')
                    messages.success(request, f'Administrador {usuario.nombre} {usuario.apellido_paterno} creado exitosamente')
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    return redirect('admin_panel')
                    
                except Exception as e:
                    messages.error(request, f'Error al crear administrador: {str(e)}')
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'errors': {'__all__': [str(e)]}})
                    return redirect('admin_panel')
                    
            elif action == 'crear_asignatura':
                try:
                    # Crear la asignatura base
                    asignatura = Asignatura.objects.create(
                        nombre=request.POST.get('nombre'),
                        nivel=request.POST.get('nivel'),
                        es_electivo=request.POST.get('es_electivo') == 'on'
                    )

                    # Crear la asignatura impartida
                    codigo = f"{asignatura.nombre[:3].upper()}{asignatura.nivel}"
                    asignatura_impartida = AsignaturaImpartida.objects.create(
                        asignatura=asignatura,
                        docente_id=request.POST.get('docente'),
                        codigo=codigo
                    )

                    # Crear la clase con el día, bloque y sala seleccionados
                    Clase.objects.create(
                        asignatura_impartida=asignatura_impartida,
                        fecha=request.POST.get('dia'),
                        bloque=request.POST.get('bloque'),
                        sala=request.POST.get('sala')
                    )

                    messages.success(request, 'Asignatura creada exitosamente')
                    return redirect('admin_panel')
                except Exception as e:
                    messages.error(request, f'Error al crear asignatura: {str(e)}')
                    return redirect('admin_panel')
            else:
                messages.error(request, 'Acción no válida')
                return redirect('admin_panel')
                
        except Exception as e:
            messages.error(request, f'Error al procesar la solicitud: {str(e)}')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            return redirect('admin_panel')

@method_decorator(login_required, name='dispatch')
class CreateAdminView(View):
    template_name = 'auth/create_admin.html'

    def get(self, request):
        if not request.user.is_admin:
            messages.error(request, 'No tienes permiso para acceder a esta página')
            return redirect('home')
        return render(request, self.template_name)

    def post(self, request):
        if not request.user.is_admin:
            messages.error(request, 'No tienes permiso para realizar esta acción')
            return redirect('home')

        try:
            # Obtener datos del formulario
            data = {
                'nombre': request.POST.get('nombre'),
                'apellido_paterno': request.POST.get('apellido_paterno'),
                'apellido_materno': request.POST.get('apellido_materno'),
                'rut': request.POST.get('rut'),
                'div': request.POST.get('div'),
                'correo': request.POST.get('correo'),
                'telefono': request.POST.get('telefono'),
                'direccion': request.POST.get('direccion'),
                'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                'password': request.POST.get('password'),
                'confirm_password': request.POST.get('confirm_password'),
                'tipo_usuario': 'ADMINISTRATIVO',
                'rol_administrativo': request.POST.get('rol', 'ADMINISTRATIVO')
            }

            # Validar datos
            es_valido, errores = validadores.validar_data_crear_usuario(data)
            if not es_valido:
                for error in errores:
                    messages.error(request, error)
                return render(request, self.template_name)

            crear_usuario(data, 'ADMINISTRATIVO')
            messages.success(request, 'Administrador creado exitosamente')
            return redirect('user_list')

        except Exception as e:
            messages.error(request, f'Error al crear administrador: {str(e)}')
            return render(request, self.template_name)

@method_decorator(csrf_exempt, name='dispatch')
class ToggleUserStatusView(View):
    def post(self, request, user_id):
        try:
            # Verificar si el usuario está autenticado
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'error': 'Usuario no autenticado'})
            
            # Verificar si el usuario es administrador
            if not hasattr(request.user, 'is_admin') or not request.user.is_admin:
                return JsonResponse({'success': False, 'error': 'No tienes permiso para realizar esta acción'})
            
            usuario = get_object_or_404(Usuario, auth_user_id=user_id)
            
            # No permitir desactivar administradores máximos
            if hasattr(usuario, 'administrativo') and usuario.administrativo.rol == 'ADMINISTRADOR_MAXIMO':
                return JsonResponse({'success': False, 'error': 'No se puede desactivar un administrador máximo'})
            
            # Invertir el estado actual
            usuario.activador = not usuario.activador
            usuario.save()
            
            # También actualizar el estado en AuthUser
            auth_user = usuario.auth_user
            auth_user.is_active = usuario.activador
            auth_user.save()
            
            return JsonResponse({
                'success': True,
                'is_active': usuario.activador
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
class AdminPanelModularView(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            return redirect('login')
        try:
            # Obtener estadísticas
            total_estudiantes = Estudiante.objects.count()
            total_profesores = Docente.objects.count()
            total_asignaturas_impartidas = AsignaturaImpartida.objects.count()
            total_administradores = Administrativo.objects.count()
            total_clases = Clase.objects.count()
            total_asignaturas = Asignatura.objects.count()
            total_cursos = Curso.objects.count()
            
            # Calcular estadísticas adicionales para el panel modular
            cursos_con_jefe = Curso.objects.filter(jefatura_actual__isnull=False).count()
            cursos_sin_jefe = total_cursos - cursos_con_jefe
            promedio_estudiantes = round(total_estudiantes / total_cursos) if total_cursos > 0 else 0
            asignaturas_sin_profesor = AsignaturaImpartida.objects.filter(docente__isnull=True).count()
            
            # Obtener todos los docentes con sus relaciones
            docentes = Docente.objects.select_related(
                'usuario',
                'especialidad'
            ).prefetch_related(
                'jefaturas'
            ).all()
            
            # Obtener todos los estudiantes
            estudiantes_sin_curso = Estudiante.objects.all().select_related('usuario', 'curso')
            
            # Obtener todos los usuarios ordenados por fecha de creación
            usuarios = Usuario.objects.all().order_by('-fecha_creacion')
            
            # Obtener todas las asignaturas con sus relaciones
            asignaturas = AsignaturaImpartida.objects.select_related(
                'asignatura',
                'docente__usuario'
            ).prefetch_related('clases').all()
            
            # Obtener cursos con sus profesores jefe y estadísticas
            cursos = Curso.objects.select_related('jefatura_actual__docente__usuario').all()
            
            # Agregar estadísticas a cada curso
            for curso in cursos:
                curso.total_estudiantes = Estudiante.objects.filter(curso=curso).count()
                curso.total_asignaturas = AsignaturaImpartida.objects.filter(clases__curso=curso).distinct().count()
            
            # Obtener todas las especialidades
            especialidades = Especialidad.objects.all()
            
            context = {
                'total_estudiantes': total_estudiantes,
                'total_profesores': total_profesores,
                'total_asignaturas_impartidas': total_asignaturas_impartidas,
                'total_administradores': total_administradores,
                'total_clases': total_clases,
                'total_asignaturas': total_asignaturas,
                'total_cursos': total_cursos,
                'cursos_con_jefe': cursos_con_jefe,
                'cursos_sin_jefe': cursos_sin_jefe,
                'promedio_estudiantes': promedio_estudiantes,
                'asignaturas_sin_profesor': asignaturas_sin_profesor,
                'docentes': docentes,
                'estudiantes_sin_curso': estudiantes_sin_curso,
                'usuarios': usuarios,
                'asignaturas': asignaturas,
                'cursos': cursos,
                'especialidades': especialidades,
            }
            return render(request, 'admin_panel_modular.html', context)
        except Exception as e:
            messages.error(request, f'Error al cargar el panel de administrador modular: {str(e)}')
            return redirect('home')

    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, 'No tienes permiso para realizar esta acción')
            return redirect('login')

        try:
            action = request.POST.get('action')
            
            if action == 'crear_curso':
                try:
                    # Validar datos
                    nivel = request.POST.get('nivel')
                    letra = request.POST.get('letra', '').upper()
                    profesor_jefe_id = request.POST.get('profesor_jefe_id')
                    
                    errores = []
                    if not nivel or not nivel.isdigit() or int(nivel) < 1 or int(nivel) > 4:
                        errores.append('El nivel debe estar entre 1 y 4')
                    
                    if not letra or letra not in ['A', 'B', 'C']:
                        errores.append('La letra debe ser A o B')
                    
                    if not profesor_jefe_id:
                        errores.append('Debe seleccionar un profesor jefe')
                    
                    # Verificar si ya existe un curso con el mismo nivel y letra
                    if Curso.objects.filter(nivel=nivel, letra=letra).exists():
                        errores.append(f'Ya existe un curso {nivel}°{letra}')
                    
                    # Verificar si el profesor ya es jefe de otro curso
                    if profesor_jefe_id:
                        docente = get_object_or_404(Docente, usuario__auth_user_id=profesor_jefe_id)
                        if docente.jefaturas.filter(curso__isnull=False).exists():
                            errores.append('El profesor seleccionado ya es jefe de otro curso')
                    
                    if errores:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': False,
                                'errors': errores
                            })
                        for error in errores:
                            messages.error(request, error)
                        return redirect('admin_panel')
                    
                    with transaction.atomic():
                        # Crear el curso
                        curso = Curso.objects.create(
                            nivel=nivel,
                            letra=letra
                        )
                        
                        # Actualizar el docente y crear la relación de profesor jefe
                        docente = get_object_or_404(Docente, usuario__auth_user_id=profesor_jefe_id)
                        docente.es_profesor_jefe = True
                        docente.save()
                        
                        ProfesorJefe.objects.create(
                            docente=docente,
                            curso=curso
                        )
                        
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': True,
                                'message': f'Curso {curso.nivel}°{curso.letra} creado exitosamente'
                            })
                        
                        messages.success(request, f'Curso {curso.nivel}°{curso.letra} creado exitosamente')
                        return redirect('admin_panel')
                        
                except Exception as e:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': [str(e)]
                        })
                    messages.error(request, f'Error al crear curso: {str(e)}')
                    return redirect('admin_panel')
            
            elif action == 'crear_estudiante':
                data = {
                    'nombre': request.POST.get('nombre'),
                    'apellido_paterno': request.POST.get('apellido_paterno'),
                    'apellido_materno': request.POST.get('apellido_materno'),
                    'rut': request.POST.get('rut'),
                    'div': request.POST.get('div'),
                    'correo': request.POST.get('correo'),
                    'telefono': request.POST.get('telefono'),
                    'direccion': request.POST.get('direccion'),
                    'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                    'password': request.POST.get('password'),
                    'contacto_emergencia': request.POST.get('contacto_emergencia'),
                    'curso': request.POST.get('curso')
                }
                
                # Validar datos
                es_valido, errores = validadores.validar_data_crear_usuario(data, tipo_usuario='ESTUDIANTE')
                if not es_valido:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': errores
                        })
                    for error in errores:
                        messages.error(request, error)
                    return redirect('admin_panel')
                
                try:
                    usuario = crear_usuario(data, 'ESTUDIANTE')
                    messages.success(request, f'Estudiante {usuario.nombre} {usuario.apellido_paterno} creado exitosamente')
                except Exception as e:
                    messages.error(request, f'Error al crear estudiante: {str(e)}')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                return redirect('admin_panel')
            
            elif action == 'crear_docente':
                data = {
                    'nombre': request.POST.get('nombre'),
                    'apellido_paterno': request.POST.get('apellido_paterno'),
                    'apellido_materno': request.POST.get('apellido_materno'),
                    'rut': request.POST.get('rut'),
                    'div': request.POST.get('div'),
                    'correo': request.POST.get('correo'),
                    'telefono': request.POST.get('telefono'),
                    'direccion': request.POST.get('direccion'),
                    'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                    'password': request.POST.get('password'),
                    'especialidad': request.POST.get('especialidad')
                }
                
                # Validar datos
                es_valido, errores = validadores.validar_data_crear_usuario(data, tipo_usuario='DOCENTE')
                if not es_valido:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': errores
                        })
                    for error in errores:
                        messages.error(request, error)
                    return redirect('admin_panel')
                
                try:
                    usuario = crear_usuario(data, 'DOCENTE')
                    messages.success(request, f'Docente {usuario.nombre} {usuario.apellido_paterno} creado exitosamente')
                except Exception as e:
                    messages.error(request, f'Error al crear docente: {str(e)}')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                return redirect('admin_panel')
            
            elif action == 'crear_administrador':
                data = {
                    'nombre': request.POST.get('nombre'),
                    'apellido_paterno': request.POST.get('apellido_paterno'),
                    'apellido_materno': request.POST.get('apellido_materno'),
                    'rut': request.POST.get('rut'),
                    'div': request.POST.get('div'),
                    'correo': request.POST.get('correo'),
                    'telefono': request.POST.get('telefono'),
                    'direccion': request.POST.get('direccion'),
                    'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
                    'password': request.POST.get('password'),
                    'rol': request.POST.get('rol')
                }
                
                # Validar datos
                es_valido, errores = validadores.validar_data_crear_usuario(data, tipo_usuario='ADMINISTRATIVO')
                if not es_valido:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': errores
                        })
                    for error in errores:
                        messages.error(request, error)
                    return redirect('admin_panel')
                
                try:
                    usuario = crear_usuario(data, 'ADMINISTRATIVO')
                    messages.success(request, f'Administrador {usuario.nombre} {usuario.apellido_paterno} creado exitosamente')
                except Exception as e:
                    messages.error(request, f'Error al crear administrador: {str(e)}')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                return redirect('admin_panel')
            
            elif action == 'crear_asignatura':
                try:
                    codigo = request.POST.get('codigo')
                    nombre = request.POST.get('nombre')
                    curso_id = request.POST.get('curso')
                    profesor_id = request.POST.get('profesor')
                    descripcion = request.POST.get('descripcion')
                    
                    errores = []
                    if not codigo:
                        errores.append('El código es obligatorio')
                    if not nombre:
                        errores.append('El nombre es obligatorio')
                    if not curso_id:
                        errores.append('Debe seleccionar un curso')
                    
                    if errores:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': False,
                                'errors': errores
                            })
                        for error in errores:
                            messages.error(request, error)
                        return redirect('admin_panel')
                    
                    # Crear la asignatura
                    asignatura = Asignatura.objects.create(
                        codigo=codigo,
                        nombre=nombre,
                        descripcion=descripcion
                    )
                    
                    # Crear la asignatura impartida
                    curso = get_object_or_404(Curso, id=curso_id)
                    docente = None
                    if profesor_id:
                        docente = get_object_or_404(Docente, usuario__auth_user_id=profesor_id)
                    
                    asignatura_impartida = AsignaturaImpartida.objects.create(
                        asignatura=asignatura,
                        docente=docente
                    )
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'message': f'Asignatura {asignatura.nombre} creada exitosamente'
                        })
                    
                    messages.success(request, f'Asignatura {asignatura.nombre} creada exitosamente')
                    return redirect('admin_panel')
                    
                except Exception as e:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'errors': [str(e)]
                        })
                    messages.error(request, f'Error al crear asignatura: {str(e)}')
                    return redirect('admin_panel')
            
            else:
                messages.error(request, 'Acción no válida')
                return redirect('admin_panel')
                
        except Exception as e:
            messages.error(request, f'Error en el panel de administrador: {str(e)}')
            return redirect('admin_panel')
