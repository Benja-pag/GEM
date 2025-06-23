@echo off
echo Iniciando el proyecto GEM...

echo Activando entorno virtual...
call .\env\Scripts\activate

echo Limpiando la base de datos...
call python manage.py flush --noinput

echo Realizando migraciones...
call python manage.py makemigrations
call python manage.py migrate

echo Poblando la base de datos...

REM 1. Datos base
echo 1. Creando administrador...
call python Poblar_database\01_datos_base\administrador_bd.py

echo 2. Creando cursos...
call python Poblar_database\01_datos_base\cursos_bd.py

echo 3. Creando docentes...
call python Poblar_database\01_datos_base\docente_bd.py

echo 4. Creando asignaturas base...
call python Poblar_database\01_datos_base\asignaturas_bd.py

echo 5. Creando alumnos...
call python Poblar_database\01_datos_base\alumnos_bd.py

REM 2. Horarios
echo 6. Poblando horarios (V3)...
call python Poblar_database\02_horarios\asignacion_horarios_unicos_v3.py

REM 3. Evaluaciones y notas
echo 7. Inscribiendo alumnos...
call python Poblar_database\03_evaluaciones\inscribir_alumnos_automatico.py

echo 8. Creando evaluaciones y notas...
call python Poblar_database\03_evaluaciones\poblar_evaluaciones_notas.py

REM 4. Asistencia
echo 9. Poblando asistencia del mes...
call python Poblar_database\04_asistencia\poblar_asistencia_mes.py

REM 5. Eventos del calendario
echo 10. Creando eventos del calendario...
call python Poblar_database\05_eventos\eventos_calendario_bd.py

REM 6. Verificaciones
echo 11. Verificando horarios...
call python Poblar_database\06_verificacion\verificar_horario.py

echo 12. Verificando evaluaciones...
call python Poblar_database\06_verificacion\verificar_evaluaciones.py

echo 13. Verificando consistencia de docentes...
call python Poblar_database\06_verificacion\verificar_consistencia_docentes.py

echo.
echo ✅ Proyecto GEM completamente poblado y listo para usar.
echo 📊 Se han creado:
echo    - Datos base (admin, cursos, docentes, asignaturas, alumnos)
echo    - Horarios con docentes por especialidad
echo    - Evaluaciones y notas
echo    - Asistencia del mes
echo    - Eventos del calendario
echo    - Verificaciones de consistencia
echo.
REM echo Iniciando servidor...
REM call python manage.py runserver
pause 