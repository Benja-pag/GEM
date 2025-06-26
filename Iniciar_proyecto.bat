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

echo 5. Creando electivos...
call python Poblar_database\01_datos_base\electivos_bd.py

echo 6. Creando alumnos...
call python Poblar_database\01_datos_base\alumnos_bd.py

REM 2. Horarios
echo 7. Poblando horarios (V3)...
call python Poblar_database\02_horarios\asignacion_horarios_unicos_v3.py

echo 8. Poblando horarios de electivos...
call python Poblar_database\02_horarios\horarios_electivos_bd.py

REM 3. Evaluaciones y notas
echo 9. Inscribiendo alumnos...
call python Poblar_database\03_evaluaciones\inscribir_alumnos_automatico.py

echo 10. Creando evaluaciones y notas...
call python Poblar_database\03_evaluaciones\poblar_evaluaciones_notas.py

REM 4. Asistencia
echo 11. Poblando asistencia del mes...
call python Poblar_database\04_asistencia\poblar_asistencia_mes.py

REM 5. Eventos del calendario
echo 12. Creando eventos del calendario...
call python Poblar_database\05_eventos\eventos_calendario_bd.py

REM 6. Actualización de fechas
echo 13. Actualizando fechas a 2025...
call python Poblar_database\09_actualizacion_fechas\actualizar_fechas_2025.py

REM 7. Foro y Comunicaciones
echo 14. Poblando foro con temas de ejemplo...
call python Poblar_database\08_foro\poblar_foro.py

echo 15. Poblando comunicaciones de ejemplo...
call python Poblar_database\08_foro\poblar_comunicaciones.py

REM 8. Verificaciones
echo 16. Verificando horarios...
call python Poblar_database\06_verificacion\verificar_horario.py

echo 17. Verificando evaluaciones...
call python Poblar_database\06_verificacion\verificar_evaluaciones.py

echo 18. Verificando consistencia de docentes...
call python Poblar_database\06_verificacion\verificar_consistencia_docentes.py

echo 19. Verificando electivos...
call python Poblar_database\06_verificacion\verificar_electivos.py

echo.
echo ✅ Proyecto GEM completamente poblado y listo para usar.
echo 📊 Se han creado:
echo    - Datos base (admin, cursos, docentes, asignaturas, electivos, alumnos)
echo    - Horarios con docentes por especialidad
echo    - Horarios de electivos para 3° y 4° medio
echo    - Evaluaciones y notas
echo    - Asistencia del mes
echo    - Eventos del calendario
echo    - Actualización de fechas a 2025
echo    - Foro con temas de ejemplo
echo    - Comunicaciones de ejemplo
echo    - Verificaciones de consistencia
echo.
REM echo Iniciando servidor...
REM call python manage.py runserver
pause 