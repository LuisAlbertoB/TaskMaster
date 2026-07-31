from django.db import models
from django.conf import settings


class Tarea(models.Model):

    # Opciones de prioridad
    PRIORIDAD_BAJA = 1
    PRIORIDAD_MEDIA = 2
    PRIORIDAD_ALTA = 3
    PRIORIDAD_CHOICES = [
        (PRIORIDAD_BAJA, 'Baja'),
        (PRIORIDAD_MEDIA, 'Media'),
        (PRIORIDAD_ALTA, 'Alta'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tareas',
        verbose_name="Usuario Propietario",
        help_text="Usuario que creó esta tarea"
    )
    titulo = models.CharField(
        max_length=255,
        verbose_name="Título",
        help_text="Título descriptivo de la tarea"
    )
    descripcion = models.TextField(
        blank=True,
        default='',
        verbose_name="Descripción",
        help_text="Descripción detallada de la tarea"
    )
    estado = models.BooleanField(
        default=False,
        verbose_name="Estado",
        help_text="False = Pendiente, True = Completada"
    )
    prioridad = models.IntegerField(
        choices=PRIORIDAD_CHOICES,
        default=PRIORIDAD_MEDIA,
        verbose_name="Prioridad",
        help_text="1 = Baja, 2 = Media, 3 = Alta"
    )
    imagen = models.ForeignKey(
        'src.Imagen',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tarea',
        verbose_name="Imagen Asociada",
        help_text="Imagen opcional vinculada a esta tarea"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        db_table = 'tareas'
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
        ordering = ['-created_at']

    def __str__(self):
        estado_label = "✅" if self.estado else "⏳"
        return f"{estado_label} {self.titulo} (de {self.user.name})"

    def delete(self, *args, **kwargs):
        """
        Override de delete() para eliminar la imagen asociada
        (y sus archivos físicos) cuando se elimina la tarea.
        """
        if self.imagen:
            self.imagen.delete()    # Dispara Imagen.delete() → elimina archivos físicos
        super().delete(*args, **kwargs)
