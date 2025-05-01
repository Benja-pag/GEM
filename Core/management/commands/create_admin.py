from django.core.management.base import BaseCommand
from Core.models import Usuario

class Command(BaseCommand):
    help = 'Crea un usuario administrador'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin123'
        
        if not Usuario.objects.filter(username=username).exists():
            user = Usuario.objects.create(
                username=username,
                email=email,
                first_name='Admin',
                last_name='User',
                rol='admin'
            )
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS('Usuario administrador creado exitosamente'))
        else:
            self.stdout.write(self.style.WARNING('El usuario administrador ya existe')) 