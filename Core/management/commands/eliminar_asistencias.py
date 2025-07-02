from django.core.management.base import BaseCommand
from Core.models import Asistencia
from django.utils import timezone
from django.db import transaction

class Command(BaseCommand):
    help = 'Elimina todas las asistencias de la base de datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma que realmente deseas eliminar todas las asistencias',
        )

    def handle(self, *args, **options):
        if not options['confirmar']:
            self.stdout.write(
                self.style.WARNING('⚠️ ADVERTENCIA: Este comando eliminará TODAS las asistencias de la base de datos.')
            )
            self.stdout.write(
                self.style.WARNING('Para confirmar, ejecuta el comando con --confirmar')
            )
            return

        try:
            with transaction.atomic():
                # Obtener el total de asistencias antes de eliminar
                total_asistencias = Asistencia.objects.count()
                
                # Eliminar todas las asistencias
                Asistencia.objects.all().delete()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Se eliminaron exitosamente {total_asistencias} registros de asistencia')
                )
                
                # Registrar la hora de eliminación
                hora_eliminacion = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S')
                self.stdout.write(
                    self.style.SUCCESS(f'📅 Hora de eliminación: {hora_eliminacion}')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al eliminar las asistencias: {str(e)}')
            ) 