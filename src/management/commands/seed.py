"""
TaskMaster — Seeder (Management Command)

Pobla la base de datos con los datos iniciales definidos en el diagrama ER:

  Seed 1 (Roles):
    id=1 → role="superuser", permission="root"

  Seed 2 (Users):
    id=1 → name="superuser", role=FK(1), password="Test1234!" (encriptada con Bcrypt)

  Seed 3 (Tags):
    1: "Programacion"
    2: "Analicis"
    3: "Diseño"
    4: "Verficacion"

Uso:
  python manage.py seed
"""

from django.core.management.base import BaseCommand
from src.models import Role, User, Tag


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos iniciales (Seeds del diagrama ER)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando proceso de seeding de base de datos...")

        # ─── SEED 1: Roles ────────────────────────────────────────────────────
        self.stdout.write("\nSeed 1: Roles")

        roles_data = [
            {'role': 'superuser', 'permission': 'root'},
        ]

        for r_data in roles_data:
            role, created = Role.objects.get_or_create(
                role=r_data['role'],
                defaults={'permission': r_data['permission']}
            )
            status_str = "creado" if created else "ya existia"
            self.stdout.write(f"  [{status_str}] Rol '{role.role}' (permission: {role.permission})")

        # ─── SEED 2: Superuser ────────────────────────────────────────────────
        self.stdout.write("\nSeed 2: Superuser")

        superuser_role = Role.objects.filter(role='superuser').first()
        superuser_name = 'superuser'

        superuser = User.objects.filter(name=superuser_name).first()
        if not superuser:
            superuser = User.objects.create_superuser(
                name=superuser_name,
                password='Test1234!',
                role=superuser_role,
            )
            self.stdout.write(f"  [creado] Superusuario '{superuser.name}' con rol {superuser.role.role} y clave inicial Test1234!")
        else:
            superuser.set_password('Test1234!')
            superuser.save()
            self.stdout.write(f"  [actualizado] Superusuario '{superuser_name}' listo con clave Test1234!")

        # ─── SEED 3: Tags ────────────────────────────────────────────────────
        self.stdout.write("\nSeed 3: Tags")

        tags_data = [
            'Programacion',
            'Analicis',
            'Diseño',
            'Verficacion',
        ]

        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(tag=tag_name)
            status_str = "creado" if created else "ya existia"
            self.stdout.write(f"  [{status_str}] Tag '{tag.tag}'")

        self.stdout.write("\nSeeding completado con exito.")
