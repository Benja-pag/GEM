from django.contrib import admin
from .models import Usuario, Administrativo, Docente, Estudiante, Asistencia, Calendario, Clase, Foro, Nota

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido_paterno', 'apellido_materno', 'rut', 'correo', 'telefono')
    list_filter = ('fecha_creacion',)
    search_fields = ('nombre', 'apellido_paterno', 'apellido_materno', 'rut', 'correo')
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido_paterno', 'apellido_materno', 'rut', 'div', 'fecha_nacimiento')
        }),
        ('Información de Contacto', {
            'fields': ('correo', 'telefono', 'direccion')
        }),
    )

@admin.register(Administrativo)
class AdministrativoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol')
    list_filter = ('rol',)
    search_fields = ('usuario__nombre', 'usuario__apellido_paterno')

@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ('usuario',)
    search_fields = ('usuario__nombre', 'usuario__apellido_paterno')

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'contacto_emergencia')
    search_fields = ('usuario__nombre', 'usuario__apellido_paterno')

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'fecha', 'estado', 'hora_registro')
    list_filter = ('estado', 'fecha')
    search_fields = ('estudiante__usuario__nombre', 'estudiante__usuario__apellido_paterno')

@admin.register(Calendario)
class CalendarioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo_evento', 'fecha_inicio', 'fecha_fin')
    list_filter = ('tipo_evento', 'fecha_inicio')
    search_fields = ('titulo', 'descripcion')

@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'docente', 'fecha', 'hora_inicio', 'hora_fin')
    list_filter = ('fecha', 'docente')
    search_fields = ('titulo', 'descripcion', 'docente__usuario__nombre')

@admin.register(Foro)
class ForoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'fecha_publicacion')
    list_filter = ('fecha_publicacion',)
    search_fields = ('titulo', 'contenido', 'autor__nombre')

@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'docente', 'tipo_evaluacion', 'nota', 'fecha_registro')
    list_filter = ('tipo_evaluacion', 'fecha_registro')
    search_fields = ('estudiante__usuario__nombre', 'docente__usuario__nombre', 'descripcion')
