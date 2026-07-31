from django.db import models


class Tag(models.Model):

    tag = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Etiqueta",
        help_text="Nombre único de la etiqueta (ej: Programacion, Diseño)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['id']

    def __str__(self):
        return self.tag
