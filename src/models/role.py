from django.db import models


class Role(models.Model):

    role = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nombre del Rol",
        help_text="Identificador único del rol (ej: superuser, editor, viewer)"
    )
    permission = models.CharField(
        max_length=50,
        verbose_name="Permiso",
        help_text="Nivel de permiso del rol (ej: root, read, write)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['id']

    def __str__(self):
        return f"{self.role} ({self.permission})"
