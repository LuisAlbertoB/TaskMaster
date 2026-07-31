import os
from rest_framework import serializers
from src.models import Imagen

# Tamaño máximo en bytes: 2MB = 2 * 1024 * 1024
MAX_IMAGE_SIZE_BYTES = 2 * 1024 * 1024
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}


class ImagenSerializer(serializers.ModelSerializer):

    imagen_url = serializers.SerializerMethodField(read_only=True)
    thumbnail_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Imagen
        fields = [
            'id',
            'imagen',
            'thumbnail',
            'imagen_url',
            'thumbnail_url',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'thumbnail', 'created_at', 'updated_at']

    def validate_imagen(self, value):
        """
        Validador personalizado para el archivo de imagen:
        1. Formato (JPG, JPEG, PNG, WEBP)
        2. Tamaño <= 2MB
        """
        if not value:
            raise serializers.ValidationError("Debe proporcionar un archivo de imagen válido.")

        # 1. Validar extensión de archivo
        ext = os.path.splitext(value.name)[1].lower().lstrip('.')
        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"Formato de imagen no permitido ('.{ext}'). "
                f"Formatos válidos: JPG, JPEG, PNG, WEBP."
            )

        # 2. Validar tamaño de archivo (<= 2MB)
        if value.size > MAX_IMAGE_SIZE_BYTES:
            size_mb = round(value.size / (1024 * 1024), 2)
            raise serializers.ValidationError(
                f"El tamaño de la imagen ({size_mb} MB) excede el límite máximo permitido de 2MB."
            )

        return value

    def get_imagen_url(self, obj):
        """Devuelve la URL absoluta completa del archivo original."""
        request = self.context.get('request')
        if obj.imagen and hasattr(obj.imagen, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None

    def get_thumbnail_url(self, obj):
        """Devuelve la URL absoluta completa de la miniatura."""
        request = self.context.get('request')
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None
