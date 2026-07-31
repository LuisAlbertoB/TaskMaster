from rest_framework import serializers
from src.models import User, Role


class RoleSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'role', 'permission']


class UserSerializer(serializers.ModelSerializer):

    role = RoleSimpleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        write_only=True,
        required=False,
        allow_null=True,
        help_text="ID del rol a asignar"
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=6,
        style={'input_type': 'password'},
        help_text="Contraseña (se encriptará con Bcrypt)"
    )

    class Meta:
        model = User
        fields = [
            'id',
            'name',
            'role',
            'role_id',
            'password',
            'is_active',
            'is_staff',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)  # Bcrypt
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # Bcrypt
        instance.save()
        return instance
