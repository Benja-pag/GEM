from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    AuthUser, Usuario, Administrativo, Docente, Estudiante,
    Asistencia, CalendarioClase, CalendarioColegio, Clase, Foro, Nota, Asignatura
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

class ClaseAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'profesor_jefe', 'sala')
    list_filter = ('profesor_jefe',)
    search_fields = ('nombre', 'sala')
    ordering = ('nombre',)

class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'clase', 'docente', 'dia', 'horario')
    list_filter = ('clase', 'docente', 'dia')
    search_fields = ('nombre', 'codigo')
    ordering = ('clase', 'dia', 'horario')

admin.site.register(AuthUser, AuthUserAdmin)
admin.site.register(Usuario)
admin.site.register(Administrativo)
admin.site.register(Docente)
admin.site.register(Estudiante)
admin.site.register(Asistencia)
admin.site.register(CalendarioClase)
admin.site.register(CalendarioColegio)
admin.site.register(Clase, ClaseAdmin)
admin.site.register(Foro)
admin.site.register(Nota)
admin.site.register(Asignatura, AsignaturaAdmin)
