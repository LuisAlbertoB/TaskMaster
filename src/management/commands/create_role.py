from django.core.management.base import BaseCommand
from src.models import Role


class Command(BaseCommand):
    help = 'Crea o actualiza un rol de usuario con su nivel de permiso'

    def add_arguments(self, parser):
        parser.add_argument(
            '--role',
            type=str,
            default='user',
            help='Nombre del rol (ej: user, editor, supervisor)'
        )
        parser.add_argument(
            '--permission',
            type=str,
            default='simple',
            help='Nivel de permiso (ej: simple, root, read)'
        )

    def handle(self, *args, **options):
        role_name = options['role'].strip()
        permission_name = options['permission'].strip()

        role, created = Role.objects.get_or_create(
            role=role_name,
            defaults={'permission': permission_name}
        )

        if not created:
            role.permission = permission_name
            role.save()
            status_str = "actualizado"
        else:
            status_str = "creado"

        self.stdout.write(
            f"[INFO] Rol '{role.role}' {status_str} exitosamente con permission='{role.permission}'."
        )
