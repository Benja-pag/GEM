from django.core.management.base import BaseCommand
from Core.models import Asignatura

class Command(BaseCommand):
    help = 'Crea asignaturas básicas para el sistema'

    def handle(self, *args, **kwargs):
        asignaturas = [
            'Matemáticas',
            'Lenguaje y Comunicación',
            'Historia',
            'Ciencias Naturales',
            'Inglés',
            'Educación Física',
            'Arte',
            'Música',
            'Tecnología',
            'Religión'
        ]

        for nombre in asignaturas:
            Asignatura.objects.get_or_create(nombre=nombre)
            self.stdout.write(self.style.SUCCESS(f'Asignatura "{nombre}" creada'))

        self.stdout.write(self.style.SUCCESS('Todas las asignaturas han sido creadas')) 