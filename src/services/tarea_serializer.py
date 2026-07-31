from rest_framework import serializers
from src.models import Tarea, Imagen, Tag, TareaHasTag
from src.services.imagen_serializer import ImagenSerializer
from src.services.tag_serializer import TagSerializer


class UserSimpleSerializer(serializers.Serializer):
    """Representación simplificada del usuario propietario de la tarea."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class TareaSerializer(serializers.ModelSerializer):

    user = UserSimpleSerializer(read_only=True)

    # Lectura de imagen anidada
    imagen = ImagenSerializer(read_only=True)

    # Opción A: Pasar ID de imagen ya existente
    imagen_id = serializers.PrimaryKeyRelatedField(
        queryset=Imagen.objects.all(),
        source='imagen',
        write_only=True,
        required=False,
        allow_null=True,
        help_text="ID de una imagen previamente subida"
    )

    # Opción B: Subir archivo de imagen directo al crear/editar la tarea
    imagen_file = serializers.ImageField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="Archivo de imagen directo a subir y asociar (JPG, PNG, WEBP <= 2MB)"
    )

    tags = serializers.SerializerMethodField(read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        required=False,
        help_text="Lista de IDs de etiquetas (tags) a asociar"
    )

    class Meta:
        model = Tarea
        fields = [
            'id',
            'user',
            'titulo',
            'descripcion',
            'estado',
            'prioridad',
            'imagen',
            'imagen_id',
            'imagen_file',
            'tags',
            'tag_ids',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_imagen_file(self, value):
        """Valida formato y tamaño (<= 2MB) usando las mismas reglas de ImagenSerializer."""
        if value:
            dummy_serializer = ImagenSerializer()
            return dummy_serializer.validate_imagen(value)
        return value

    def get_tags(self, obj):
        """Obtiene la lista de tags asociados a la tarea vía la tabla pivote TareaHasTag."""
        tags = Tag.objects.filter(tag_tareas__tarea=obj)
        return TagSerializer(tags, many=True).data

    def create(self, validated_data):
        """Crea la tarea, procesa la imagen directa si existe y asigna tags M:N."""
        imagen_file = validated_data.pop('imagen_file', None)
        tag_ids = validated_data.pop('tag_ids', [])

        # Si enviaron un archivo de imagen directo, crear la instancia de Imagen
        if imagen_file:
            nueva_imagen = Imagen.objects.create(imagen=imagen_file)
            validated_data['imagen'] = nueva_imagen

        tarea = Tarea.objects.create(**validated_data)

        # Crear registros pivote TareaHasTag
        for tag in tag_ids:
            TareaHasTag.objects.get_or_create(tarea=tarea, tag=tag)

        return tarea

    def update(self, instance, validated_data):
        """Actualiza la tarea, reemplaza imagen si se subió un nuevo archivo y sincroniza tags."""
        imagen_file = validated_data.pop('imagen_file', None)
        tag_ids = validated_data.pop('tag_ids', None)

        # Si se sube una nueva imagen directa, crear y reemplazar la anterior
        if imagen_file:
            if instance.imagen:
                instance.imagen.delete()  # Borra archivo físico anterior
            nueva_imagen = Imagen.objects.create(imagen=imagen_file)
            validated_data['imagen'] = nueva_imagen

        # Actualizar campos sencillos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Sincronizar tags si se proporcionó tag_ids en la petición
        if tag_ids is not None:
            TareaHasTag.objects.filter(tarea=instance).delete()
            for tag in tag_ids:
                TareaHasTag.objects.create(tarea=instance, tag=tag)

        return instance
