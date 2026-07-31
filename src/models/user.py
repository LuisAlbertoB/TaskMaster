from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
   
    def create_user(self, name, password=None, **extra_fields):
        """Crea y retorna un usuario normal."""
        if not name:
            raise ValueError('El campo "name" es obligatorio.')
        user = self.model(name=name, **extra_fields)
        if password:
            user.set_password(password)      # Hashea con Bcrypt (settings.PASSWORD_HASHERS)
        else:
            user.set_unusable_password()      # Marca la contraseña como no establecida
        user.save(using=self._db)
        return user

    def create_superuser(self, name, password=None, **extra_fields):
        """Crea y retorna un superusuario Django (para manage.py createsuperuser)."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    role = models.ForeignKey(
        'src.Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Rol",
        help_text="Rol asignado al usuario que determina sus permisos"
    )
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Nombre de Usuario",
        help_text="Identificador único usado para iniciar sesión"
    )

    # Campos requeridos por Django para el admin y permisos
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_staff = models.BooleanField(default=False, verbose_name="Es Staff")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última modificación")

    objects = UserManager()

    # Configuración de autenticación
    USERNAME_FIELD = 'name'     # Campo usado para login
    REQUIRED_FIELDS = []        # Campos extra para createsuperuser (name se pide siempre)

    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']

    def __str__(self):
        role_name = self.role.role if self.role else "Sin Rol"
        return f"{self.name} ({role_name})"
