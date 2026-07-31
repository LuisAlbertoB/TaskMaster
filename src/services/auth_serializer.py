from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        """Agrega claims personalizados al payload del JWT."""
        token = super().get_token(user)

        # Claims personalizados visibles al decodificar el token
        token['name'] = user.name
        token['role'] = user.role.role if user.role else None
        token['permission'] = user.role.permission if user.role else None
        token['is_staff'] = user.is_staff

        return token

    def validate(self, attrs):
        """Enriquece la respuesta JSON con datos del usuario autenticado."""
        data = super().validate(attrs)

        # Datos adicionales en la respuesta (no en el token, sino en el JSON)
        data['user'] = {
            'id': self.user.id,
            'name': self.user.name,
            'role': self.user.role.role if self.user.role else None,
            'permission': self.user.role.permission if self.user.role else None,
        }

        return data
