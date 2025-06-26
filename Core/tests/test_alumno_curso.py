from django.test import TestCase
from Core.models import (
    AuthUser, Usuario, Curso, Estudiante, Asignatura, Docente, Especialidad,
    AsignaturaImpartida, AsignaturaInscrita, Clase, Asistencia
)

class AlumnoCursoTest(TestCase):
    def setUp(self):
        self.auth_user = AuthUser.objects.create_user(rut="12345678", div="9", password="testpass")
        self.usuario = Usuario.objects.create(
            rut="12345678",
            div="9",
            nombre="Juan",
            apellido_paterno="Pérez",
            apellido_materno="González",
            correo="juan.perez@example.com",
            telefono="123456789",
            direccion="Calle Falsa 123",
            fecha_nacimiento="2005-01-01",
            auth_user=self.auth_user,
            password="testpass"
        )
        self.curso = Curso.objects.create(nivel=1, letra='D')

    def test_agregar_alumno_a_curso(self):
        print("\n[TEST] test_agregar_alumno_a_curso: INICIADO")
        alumno = Estudiante.objects.create(
            usuario=self.usuario,
            contacto_emergencia="987654321",
            curso=self.curso
        )
        print(f"Alumno creado: {alumno.usuario.nombre} en curso {alumno.curso}")
        self.assertEqual(alumno.curso, self.curso)
        self.assertEqual(alumno.usuario.nombre, "Juan")
        print("[TEST] test_agregar_alumno_a_curso: OK")

    def test_eliminar_curso_deja_alumno_sin_curso(self):
        print("\n[TEST] test_eliminar_curso_deja_alumno_sin_curso: INICIADO")
        alumno = Estudiante.objects.create(
            usuario=self.usuario,
            contacto_emergencia="987654321",
            curso=self.curso
        )
        self.curso.delete()
        alumno.refresh_from_db()
        print(f"Alumno {alumno.usuario.nombre} después de eliminar curso: curso={alumno.curso}")
        self.assertIsNone(alumno.curso)
        print("[TEST] test_eliminar_curso_deja_alumno_sin_curso: OK")

    def test_no_inscribir_dos_veces_en_misma_asignatura(self):
        print("\n[TEST] test_no_inscribir_dos_veces_en_misma_asignatura: INICIADO")
        auth_user_doc = AuthUser.objects.create_user(rut="87654321", div="K", password="testpass")
        usuario_doc = Usuario.objects.create(
            rut="87654321",
            div="K",
            nombre="Ana",
            apellido_paterno="Soto",
            apellido_materno="López",
            correo="ana.soto@example.com",
            telefono="987654321",
            direccion="Calle Real 456",
            fecha_nacimiento="1980-05-10",
            auth_user=auth_user_doc,
            password="testpass"
        )
        especialidad = Especialidad.objects.create(nombre="Matemáticas")
        docente = Docente.objects.create(usuario=usuario_doc, especialidad=especialidad)
        asignatura = Asignatura.objects.create(nombre="Matemáticas", nivel=1)
        asignatura_imp = AsignaturaImpartida.objects.create(asignatura=asignatura, docente=docente, codigo="MAT101")

        alumno = Estudiante.objects.create(
            usuario=self.usuario,
            contacto_emergencia="987654321",
            curso=self.curso
        )
        AsignaturaInscrita.objects.create(estudiante=alumno, asignatura_impartida=asignatura_imp)
        print(f"Alumno {alumno.usuario.nombre} inscrito en {asignatura_imp}")
        with self.assertRaises(Exception):
            AsignaturaInscrita.objects.create(estudiante=alumno, asignatura_impartida=asignatura_imp)
        print("[TEST] test_no_inscribir_dos_veces_en_misma_asignatura: OK")

    def test_clases_y_asistencia_alumno(self):
        print("\n[TEST] test_clases_y_asistencia_alumno: INICIADO")
        # Crear docente y asignatura
        auth_user_doc = AuthUser.objects.create_user(rut="87654321", div="K", password="testpass")
        usuario_doc = Usuario.objects.create(
            rut="87654321",
            div="K",
            nombre="Ana",
            apellido_paterno="Soto",
            apellido_materno="López",
            correo="ana.soto@example.com",
            telefono="987654321",
            direccion="Calle Real 456",
            fecha_nacimiento="1980-05-10",
            auth_user=auth_user_doc,
            password="testpass"
        )
        especialidad = Especialidad.objects.create(nombre="Matemáticas")
        docente = Docente.objects.create(usuario=usuario_doc, especialidad=especialidad)
        asignatura = Asignatura.objects.create(nombre="Matemáticas", nivel=1)
        asignatura_imp = AsignaturaImpartida.objects.create(asignatura=asignatura, docente=docente, codigo="MAT101")

        alumno = Estudiante.objects.create(
            usuario=self.usuario,
            contacto_emergencia="987654321",
            curso=self.curso
        )
        AsignaturaInscrita.objects.create(estudiante=alumno, asignatura_impartida=asignatura_imp)

        # Crear dos clases para la asignatura
        clase1 = Clase.objects.create(
            asignatura_impartida=asignatura_imp,
            curso=self.curso,
            fecha="LUNES",
            horario="08:00-09:30",
            sala="SALA_1"
        )
        clase2 = Clase.objects.create(
            asignatura_impartida=asignatura_imp,
            curso=self.curso,
            fecha="MIERCOLES",
            horario="10:00-11:30",
            sala="SALA_2"
        )

        # Registrar asistencia solo en la primera clase
        asistencia = Asistencia.objects.create(
            clase=clase1,
            estudiante=alumno,
            presente=True
        )

        print(f"Asistencia de {alumno.usuario.nombre} en clase del día {clase1.fecha}: {'Presente' if asistencia.presente else 'Ausente'}")
        self.assertEqual(asistencia.clase, clase1)
        self.assertTrue(asistencia.presente)
        self.assertEqual(asistencia.estudiante, alumno)
        self.assertEqual(Clase.objects.count(), 2)
        self.assertEqual(Asistencia.objects.filter(estudiante=alumno).count(), 1)
        print("[TEST] test_clases_y_asistencia_alumno: OK")

    def test_evaluacion_y_nota_en_clase(self):
        print("\n[TEST] test_evaluacion_y_nota_en_clase: INICIADO")
        # Crear docente y asignatura
        auth_user_doc = AuthUser.objects.create_user(rut="87654321", div="K", password="testpass")
        usuario_doc = Usuario.objects.create(
            rut="87654321",
            div="K",
            nombre="Ana",
            apellido_paterno="Soto",
            apellido_materno="López",
            correo="ana.soto@example.com",
            telefono="987654321",
            direccion="Calle Real 456",
            fecha_nacimiento="1980-05-10",
            auth_user=auth_user_doc,
            password="testpass"
        )
        especialidad = Especialidad.objects.create(nombre="Matemáticas")
        docente = Docente.objects.create(usuario=usuario_doc, especialidad=especialidad)
        asignatura = Asignatura.objects.create(nombre="Matemáticas", nivel=1)
        asignatura_imp = AsignaturaImpartida.objects.create(asignatura=asignatura, docente=docente, codigo="MAT101")

        alumno = Estudiante.objects.create(
            usuario=self.usuario,
            contacto_emergencia="987654321",
            curso=self.curso
        )
        AsignaturaInscrita.objects.create(estudiante=alumno, asignatura_impartida=asignatura_imp)

        # Crear una clase para la asignatura
        clase = Clase.objects.create(
            asignatura_impartida=asignatura_imp,
            curso=self.curso,
            fecha="LUNES",
            horario="08:00-09:30",
            sala="SALA_1"
        )

        # Crear EvaluacionBase
        from Core.models import EvaluacionBase, Evaluacion, AlumnoEvaluacion
        evaluacion_base = EvaluacionBase.objects.create(
            nombre="Prueba 1",
            descripcion="Prueba de contenidos",
            asignatura=asignatura,
            ponderacion=30
        )

        # Crear una evaluación asociada a la clase y la base
        evaluacion = Evaluacion.objects.create(
            evaluacion_base=evaluacion_base,
            clase=clase,
            fecha="2024-06-25"
        )

        # Asignar una nota al alumno en esa evaluación
        nota = AlumnoEvaluacion.objects.create(
            evaluacion=evaluacion,
            estudiante=alumno,
            nota=6.5
        )

        print(f"Nota de {alumno.usuario.nombre} en {asignatura.nombre} en evaluación '{evaluacion_base.nombre}' de la clase del día {clase.fecha} es {nota.nota}")
        self.assertEqual(nota.evaluacion, evaluacion)
        self.assertEqual(nota.estudiante, alumno)
        self.assertEqual(nota.nota, 6.5)
        print("[TEST] test_evaluacion_y_nota_en_clase: OK")

    def test_asistencia_justificada(self):
        print("\n[TEST] test_asistencia_justificada: INICIADO")
        # Crear docente y asignatura
        auth_user_doc = AuthUser.objects.create_user(rut="87654321", div="K", password="testpass")
        usuario_doc = Usuario.objects.create(
            rut="87654321",
            div="K",
            nombre="Ana",
            apellido_paterno="Soto",
            apellido_materno="López",
            correo="ana.soto@example.com",
            telefono="987654321",
            direccion="Calle Real 456",
            fecha_nacimiento="1980-05-10",
            auth_user=auth_user_doc,
            password="testpass"
        )
        especialidad = Especialidad.objects.create(nombre="Matemáticas")
        docente = Docente.objects.create(usuario=usuario_doc, especialidad=especialidad)
        asignatura = Asignatura.objects.create(nombre="Matemáticas", nivel=1)
        asignatura_imp = AsignaturaImpartida.objects.create(asignatura=asignatura, docente=docente, codigo="MAT101")

        alumno = Estudiante.objects.create(
            usuario=self.usuario,
            contacto_emergencia="987654321",
            curso=self.curso
        )
        AsignaturaInscrita.objects.create(estudiante=alumno, asignatura_impartida=asignatura_imp)

        # Crear una clase para la asignatura
        clase = Clase.objects.create(
            asignatura_impartida=asignatura_imp,
            curso=self.curso,
            fecha="LUNES",
            horario="08:00-09:30",
            sala="SALA_1"
        )

        # Registrar asistencia justificada
        asistencia = Asistencia.objects.create(
            clase=clase,
            estudiante=alumno,
            presente=False,
            justificado=True,
            observaciones="Licencia médica"
        )

        print(f"Asistencia justificada: {asistencia.justificado}, Observaciones: {asistencia.observaciones}")
        self.assertFalse(asistencia.presente)
        self.assertTrue(asistencia.justificado)
        self.assertEqual(asistencia.observaciones, "Licencia médica")
        print("[TEST] test_asistencia_justificada: OK")