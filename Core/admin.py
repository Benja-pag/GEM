from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    AuthUser, Usuario, Administrativo, Docente, Estudiante,
    Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, Asignatura, ClaseCancelada
)

class AuthUserAdmin(UserAdmin):
    list_display = ('rut', 'div', 'is_active', 'is_admin', 'date_joined')
    list_filter = ('is_active', 'is_admin')
    search_fields = ('rut',)
    ordering = ('rut',)
    fieldsets = (
        (None, {'fields': ('rut', 'div', 'password')}),
        ('Permisos', {'fields': ('is_active', 'is_admin', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('rut', 'div', 'password1', 'password2', 'is_active', 'is_admin')}
        ),
    )

class ClaseCanceladaAdmin(admin.ModelAdmin):
    list_display = ('docente', 'asignatura_impartida', 'fecha_cancelacion', 'hora_cancelacion', 'motivo', 'clase_recuperada', 'fecha_registro')
    list_filter = ('motivo', 'clase_recuperada', 'fecha_cancelacion', 'fecha_registro')
    search_fields = ('docente__usuario__nombre', 'docente__usuario__apellido_paterno', 'asignatura_impartida__asignatura__nombre')
    ordering = ('-fecha_cancelacion', '-hora_cancelacion')
    readonly_fields = ('fecha_registro',)
    fieldsets = (
        ('Información Básica', {
            'fields': ('docente', 'asignatura_impartida', 'fecha_cancelacion', 'hora_cancelacion')
        }),
        ('Motivo y Descripción', {
            'fields': ('motivo', 'descripcion')
        }),
        ('Estado', {
            'fields': ('notificado_estudiantes', 'clase_recuperada', 'fecha_recuperacion')
        }),
        ('Metadatos', {
            'fields': ('fecha_registro',),
            'classes': ('collapse',)
        }),
    )

# class ClaseAdmin(admin.ModelAdmin):
#     list_display = ('nombre', 'profesor_jefe', 'sala')
#     list_filter = ('profesor_jefe',)
#     search_fields = ('nombre', 'sala')
#     ordering = ('nombre',)

# class AsignaturaAdmin(admin.ModelAdmin):
#     list_display = ('nombre', 'clase', 'docente', 'dia', 'horario')
#     list_filter = ('clase', 'docente', 'dia')
#     search_fields = ('nombre', 'codigo')
#     ordering = ('clase', 'dia', 'horario')

admin.site.register(AuthUser, AuthUserAdmin)
admin.site.register(Usuario)
admin.site.register(Administrativo)
admin.site.register(Docente)
admin.site.register(Estudiante)
admin.site.register(Asistencia)
admin.site.register(CalendarioClase)
admin.site.register(CalendarioColegio)
admin.site.register(Clase)
admin.site.register(Foro)
admin.site.register(Asignatura)
admin.site.register(ClaseCancelada, ClaseCanceladaAdmin)
