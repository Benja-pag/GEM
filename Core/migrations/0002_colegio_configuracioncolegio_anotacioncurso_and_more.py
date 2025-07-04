# Generated by Django 5.2.1 on 2025-06-13 10:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Colegio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('direccion', models.CharField(blank=True, max_length=200, null=True)),
                ('telefono', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('director', models.CharField(blank=True, max_length=100, null=True)),
                ('rut', models.CharField(help_text='Ej: 12.345.678-9', max_length=12, unique=True)),
                ('fecha_fundacion', models.DateField(blank=True, null=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ConfiguracionColegio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_colegio', models.CharField(max_length=200)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='logos/')),
                ('ano_academico', models.PositiveIntegerField()),
                ('fecha_inicio', models.DateField()),
                ('fecha_termino', models.DateField()),
                ('activo', models.BooleanField(default=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Configuración del Colegio',
                'verbose_name_plural': 'Configuraciones del Colegio',
            },
        ),
        migrations.CreateModel(
            name='AnotacionCurso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField()),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('es_publica', models.BooleanField(default=True)),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Core.usuario')),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='anotaciones', to='Core.curso')),
            ],
        ),
        migrations.CreateModel(
            name='LogActividad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('CREACION', 'Creación'), ('ACTUALIZACION', 'Actualización'), ('ELIMINACION', 'Eliminación'), ('LOGIN', 'Inicio de Sesión'), ('LOGOUT', 'Cierre de Sesión'), ('OTRO', 'Otro')], max_length=20)),
                ('accion', models.CharField(max_length=200)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('detalles', models.JSONField(blank=True, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Core.usuario')),
            ],
            options={
                'verbose_name': 'Registro de Actividad',
                'verbose_name_plural': 'Registros de Actividad',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='MaterialClase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('descripcion', models.TextField()),
                ('archivo', models.FileField(blank=True, null=True, upload_to='materiales_clase/')),
                ('fecha_publicacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('clase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materiales', to='Core.clase')),
            ],
        ),
        migrations.CreateModel(
            name='ObjetivoAsignatura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField()),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('completado', models.BooleanField(default=False)),
                ('asignatura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='objetivos', to='Core.asignatura')),
            ],
        ),
        migrations.CreateModel(
            name='RecursoAsignatura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('tipo', models.CharField(choices=[('DOCUMENTO', 'Documento'), ('VIDEO', 'Video'), ('ENLACE', 'Enlace'), ('OTRO', 'Otro')], max_length=20)),
                ('descripcion', models.TextField()),
                ('url', models.URLField(blank=True, null=True)),
                ('archivo', models.FileField(blank=True, null=True, upload_to='recursos_asignatura/')),
                ('fecha_publicacion', models.DateTimeField(auto_now_add=True)),
                ('asignatura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recursos', to='Core.asignatura')),
            ],
        ),
        migrations.CreateModel(
            name='Tarea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('descripcion', models.TextField()),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_entrega', models.DateTimeField()),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('EN_CURSO', 'En Curso'), ('ENTREGADA', 'Entregada'), ('CALIFICADA', 'Calificada')], default='PENDIENTE', max_length=20)),
                ('asignatura_impartida', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tareas', to='Core.asignaturaimpartida')),
            ],
        ),
    ]
