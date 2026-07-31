import os
from io import BytesIO
from django.db import models
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from PIL import Image as PilImage


class Imagen(models.Model):

    imagen = models.ImageField(
        upload_to='tareas/originales/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name="Imagen",
        help_text="Archivo de imagen (JPG, PNG o WEBP). Máximo recomendado: 5MB."
    )
    thumbnail = models.ImageField(
        upload_to='tareas/thumbnails/',
        blank=True,
        null=True,
        editable=False,
        verbose_name="Miniatura",
        help_text="Versión miniatura generada automáticamente (300x300px max)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de subida")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        db_table = 'imagenes'
        verbose_name = 'Imagen'
        verbose_name_plural = 'Imágenes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Imagen #{self.pk} — {os.path.basename(self.imagen.name) if self.imagen else 'Sin archivo'}"

    def save(self, *args, **kwargs):

        # Si es una actualización y la imagen cambió, eliminar archivos anteriores
        if self.pk:
            try:
                old_instance = Imagen.objects.get(pk=self.pk)
                if old_instance.imagen and old_instance.imagen != self.imagen:
                    old_instance.imagen.delete(save=False)
                if old_instance.thumbnail:
                    old_instance.thumbnail.delete(save=False)
            except Imagen.DoesNotExist:
                pass

        # Primer guardado para que el archivo de imagen exista en disco
        super().save(*args, **kwargs)

        # Generar thumbnail si hay imagen
        if self.imagen:
            self._generate_thumbnail()

    def _generate_thumbnail(self):
        """Genera una versión miniatura de la imagen usando Pillow (300x300px max)."""
        try:
            img = PilImage.open(self.imagen.path)
            img.thumbnail((300, 300), PilImage.LANCZOS)

            # Determinar formato de salida
            img_format = img.format or 'JPEG'
            if img_format.upper() == 'WEBP':
                ext = 'webp'
                content_type = 'image/webp'
            elif img_format.upper() == 'PNG':
                ext = 'png'
                content_type = 'image/png'
            else:
                ext = 'jpg'
                content_type = 'image/jpeg'
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')

            # Guardar thumbnail en buffer
            thumb_io = BytesIO()
            img.save(thumb_io, format=img_format.upper() if img_format.upper() != 'JPG' else 'JPEG', quality=85)
            thumb_io.seek(0)

            # Nombre del archivo thumbnail
            base_name = os.path.splitext(os.path.basename(self.imagen.name))[0]
            thumb_name = f"thumb_{base_name}.{ext}"

            # Guardar sin disparar save() recursivo
            self.thumbnail.save(thumb_name, ContentFile(thumb_io.read()), save=False)
            Imagen.objects.filter(pk=self.pk).update(thumbnail=self.thumbnail.name)
        except Exception as e:
            # Si falla la generación del thumbnail, no es un error crítico
            pass

    def delete(self, *args, **kwargs):

        # Eliminar archivo de imagen original
        if self.imagen:
            self.imagen.delete(save=False)
        # Eliminar archivo de thumbnail
        if self.thumbnail:
            self.thumbnail.delete(save=False)
        super().delete(*args, **kwargs)
