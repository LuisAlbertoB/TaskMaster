from rest_framework import permissions


class IsRootUser(permissions.BasePermission):

    message = "Acceso denegado. Se requiere permiso 'root'."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Acceso directo si es superuser de Django
        if request.user.is_superuser:
            return True

        # Verificar que el rol del usuario tenga permission="root"
        return (
            request.user.role is not None
            and request.user.role.permission == 'root'
        )


class IsOwner(permissions.BasePermission):

    message = "No tienes permiso para acceder a este recurso. Solo el propietario puede hacerlo."

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Los usuarios root tienen acceso total
        if request.user.is_superuser:
            return True
        if request.user.role and request.user.role.permission == 'root':
            return True

        # Verificar que el usuario autenticado sea el propietario
        return hasattr(obj, 'user') and obj.user == request.user
