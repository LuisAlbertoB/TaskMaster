from rest_framework import viewsets, permissions
from src.models import User
from src.services.user_serializer import UserSerializer
from src.middlewares.permissions import IsRootUser


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión CRUD de Usuarios.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        is_root = (
            user.is_superuser or
            (user.role is not None and user.role.permission == 'root')
        )

        if is_root:
            return User.objects.all()
        # Usuario normal solo ve su propio registro
        return User.objects.filter(id=user.id)
