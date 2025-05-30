call python manage.py flush --noinput
call python manage.py makemigrations
call python manage.py migrate
call python Poblar_database\administrador_bd.py
call python Poblar_database\asignaturas_bd.py
call python Poblar_database\cursos_bd.py
call python Poblar_database\docente_bd.py
call python Poblar_database\alumnos_bd.py
call .\env\Scripts\activate
call python manage.py runserver 