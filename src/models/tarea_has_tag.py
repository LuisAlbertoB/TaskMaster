from django.db import models


class TareaHasTag(models.Model):

    tarea = models.ForeignKey(
        'src.Tarea',
        on_delete=models.CASCADE,
        related_name='tarea_tags',
        verbose_name="Tarea"
    )
    tag = models.ForeignKey(
        'src.Tag',
        on_delete=models.CASCADE,
        related_name='tag_tareas',
        verbose_name="Tag"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de asignación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        db_table = 'tareas_has_tags'
        verbose_name = 'Tarea-Tag'
        verbose_name_plural = 'Tareas-Tags'
        # Evitar que la misma tarea tenga el mismo tag duplicado
        unique_together = ('tarea', 'tag')
        ordering = ['-created_at']

    def __str__(self):
        return f"Tarea #{self.tarea_id} ↔ Tag '{self.tag.tag}'"
