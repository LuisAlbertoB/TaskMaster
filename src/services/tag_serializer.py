from rest_framework import serializers
from src.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer para crear, listar y editar etiquetas.
    """
    class Meta:
        model = Tag
        fields = ['id', 'tag', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_tag(self, value):
        """Limpia y valida el nombre del tag."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("El nombre del tag no puede estar vacío.")
        return value
