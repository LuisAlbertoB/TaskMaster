from django.core.management.base import BaseCommand
from src.models import Role, User, Tag


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos iniciales (Seeds del diagrama ER)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING(
            "🌱 Iniciando proceso de seeding de base de datos..."
        ))

        # ─── SEED 1: Roles ────────────────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n📋 Seed 1: Roles"))

        roles_data = [
            {'role': 'superuser', 'permission': 'root'},
        ]

        for r_data in roles_data:
            role, created = Role.objects.get_or_create(
                role=r_data['role'],
                defaults={'permission': r_data['permission']}
            )
            status = "✓ creado" if created else "- ya existía"
            self.stdout.write(self.style.SUCCESS(
                f"  {status}: Rol '{role.role}' (permission: {role.permission})"
            ))

        # ─── SEED 2: Superuser (sin contraseña) ──────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n👤 Seed 2: Superuser"))

        superuser_role = Role.objects.filter(role='superuser').first()
        superuser_name = 'superuser'

        if not User.objects.filter(name=superuser_name).exists():
            # Crear superusuario SIN contraseña (set_unusable_password)
            # La contraseña se establecerá vía PUT en un futuro endpoint.
            superuser = User.objects.create_superuser(
                name=superuser_name,
                password=None,          # Sin contraseña — se usa set_unusable_password()
                role=superuser_role,
            )
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ Superusuario creado: '{superuser.name}' "
                f"(rol: {superuser.role.role}, sin contraseña establecida)"
            ))
            self.stdout.write(self.style.WARNING(
                f"    ⚠ Recuerda establecer la contraseña vía PUT /api/users/{superuser.pk}/ "
                f"o con: python manage.py changepassword {superuser.name}"
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f"  - Superusuario '{superuser_name}' ya existe."
            ))

        # ─── SEED 3: Tags ────────────────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n🏷️  Seed 3: Tags"))

        tags_data = [
            'Programacion',
            'Analicis',
            'Diseño',
            'Verficacion',
        ]

        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(tag=tag_name)
            status = "✓ creado" if created else "- ya existía"
            self.stdout.write(self.style.SUCCESS(f"  {status}: Tag '{tag.tag}'"))

        # ─── Resumen ─────────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS(
            "\n🎉 ¡Seeding completado con éxito!"
        ))
