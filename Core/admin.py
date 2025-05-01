from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Curso, EstudianteCurso, Calificacion

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff')
    list_filter = ('rol', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'fecha_nacimiento', 'telefono', 'direccion')}),
    )

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'profesor', 'fecha_inicio', 'fecha_fin')
    list_filter = ('profesor', 'fecha_inicio', 'fecha_fin')
    search_fields = ('nombre', 'descripcion')

@admin.register(EstudianteCurso)
class EstudianteCursoAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'curso', 'fecha_inscripcion')
    list_filter = ('curso', 'fecha_inscripcion')
    search_fields = ('estudiante__username', 'curso__nombre')

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'curso', 'nota', 'fecha')
    list_filter = ('curso', 'fecha')
    search_fields = ('estudiante__username', 'curso__nombre')
