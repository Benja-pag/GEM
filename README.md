"# GEM" 

HTMLS:
"admin_panel": Panel de control para el administrador: gestionar usuarios, asignaturas, encuestas, calendario, etc
"attecendance": Registro de asistencia de los alumnos por asignatura o curso.
"calendar": Visualización del calendario académico del estudiante o profesor.
"class": seguimiento de contenidos de una materia.
"dashboard": Página principal después de iniciar sesión.
"forum": Foro de discusión para temas académicos entre alumnos y profesores.
"home": Página pública de bienvenida al sistema (antes del login).
"login": Formulario de inicio de sesión.
"messages": Sistema de mensajes privados entre usuarios (profesores/alumnos).
"notifications": Centro de notificaciones del usuario.
"password_reset": Formulario para solicitar recuperación de contraseña.
"profile": Perfil del usuario.
"reguster": Formulario de creación de cuenta.
"subjetcs": Listado de asignaturas del usuario.
"surveys": Encuestas académicas (satisfacción de curso, feedback de profesores, etc.).
"tasks": Gestión de tareas académicas del estudiante.
"test": Evaluaciones o exámenes online.


Jesus:
admin_panel
login
password_reset

Ignacio:
forum
subjetcs
class
[Al precionar una clase en "Subjects" debe mandarte a clase seleccionada]

Benjamin:
attecendance
messages
models.py


comando:
python manage.py runserver (Para iniciar)
python manage.py migrate
cls (limpiar la terminal)
python manage.py makemigrations (pasar tablas a la base de datos)


sitios:
http://localhost:8000/asistencia/

Para crear la base de datos:
[Primero debes crear tu usuario que sea el por defecto "postgres"]
[Segundo la contraseña debe ser si o si "gem1234"]
[Tercero entrar a seleccionar sql shell]
[Cuarto ingresar con el usuario]
[quinto crear la base de datos con este comando "CREATE DATABASE GEM"]

Comando habituales:
\c gem (para entrar la base de datos)
\l (Listar todas las base de datos)
\dt (para lista las tablas)

otro comando : 
SELECT * FROM "public"."Core_usuario";


Correo: admin@gem.cl
Contraseña: admin123s