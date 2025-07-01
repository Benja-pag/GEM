import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from django.db import transaction
from Core.models import Curso, AsignaturaImpartida, Comunicacion, AnotacionCurso, Estudiante, Clase, AsignaturaInscrita

def eliminar_curso_4c():
    try:
        # Buscar el curso 4°C
        curso = Curso.objects.filter(nivel=4, letra='C').first()
        if not curso:
            print("El curso 4°C no existe.")
            return

        # Verificar si hay estudiantes
        estudiantes = Estudiante.objects.filter(curso=curso)
        if estudiantes.exists():
            print(f"Error: El curso tiene {estudiantes.count()} estudiantes asignados. Debes reasignarlos primero.")
            return

        with transaction.atomic():
            # 1. Eliminar todas las clases asociadas al curso
            clases = Clase.objects.filter(curso=curso)
            num_clases = clases.count()
            clases.delete()
            print(f"Se eliminaron {num_clases} clases.")

            # 2. Eliminar todas las comunicaciones del curso
            comunicaciones = Comunicacion.objects.filter(destinatarios_cursos=curso)
            num_comunicaciones = comunicaciones.count()
            comunicaciones.delete()
            print(f"Se eliminaron {num_comunicaciones} comunicaciones.")

            # 3. Eliminar todas las anotaciones del curso
            anotaciones = AnotacionCurso.objects.filter(curso=curso)
            num_anotaciones = anotaciones.count()
            anotaciones.delete()
            print(f"Se eliminaron {num_anotaciones} anotaciones.")

            # 4. Eliminar la jefatura si existe
            if hasattr(curso, 'jefatura_actual') and curso.jefatura_actual:
                profesor_jefe = curso.jefatura_actual.docente
                curso.jefatura_actual.delete()
                # Si el profesor no tiene otras jefaturas, desmarcar es_profesor_jefe
                if not profesor_jefe.jefaturas.exists():
                    profesor_jefe.es_profesor_jefe = False
                    profesor_jefe.save()
                print("Se eliminó la jefatura del curso.")

            # 5. Finalmente eliminar el curso
            curso.delete()
            print("Curso 4°C eliminado exitosamente.")

    except Exception as e:
        print(f"Error al eliminar el curso: {str(e)}")

if __name__ == '__main__':
    eliminar_curso_4c() 