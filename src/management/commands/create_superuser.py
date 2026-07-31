from django.core.management.base import BaseCommand
from src.models import Role, User


class Command(BaseCommand):
    help = 'Crear el superusuario por defecto (superuser / Test1234!) si no existe'

    def handle(self, *args, **options):
        superuser_name = 'superuser'
        default_password = 'Test1234!'

        # Asegurar que el rol superuser exista
        superuser_role, _ = Role.objects.get_or_create(
            role='superuser',
            defaults={'permission': 'root'}
        )

        user = User.objects.filter(name=superuser_name).first()

        if user:
            self.stdout.write(
                self.style.WARNING(f"El superusuario '{superuser_name}' ya existe.")
            )
        else:
            User.objects.create_superuser(
                name=superuser_name,
                password=default_password,
                role=superuser_role,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superusuario '{superuser_name}' creado exitosamente con la contraseña por defecto '{default_password}'."
                )
            )
