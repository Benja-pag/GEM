from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    AuthUser, Usuario, Administrativo, Docente, Estudiante,
    Asistencia, CalendarioClase, Clase, Foro, Nota
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

admin.site.register(AuthUser, AuthUserAdmin)
admin.site.register(Usuario)
admin.site.register(Administrativo)
admin.site.register(Docente)
admin.site.register(Estudiante)
admin.site.register(Asistencia)
admin.site.register(CalendarioClase)
admin.site.register(Clase)
admin.site.register(Foro)
admin.site.register(Nota)
