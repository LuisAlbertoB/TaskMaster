from rest_framework import permissions


class IsRootUser(permissions.BasePermission):
    """
    Permiso que solo permite acceso a usuarios cuyo rol tiene permission="root".
    Equivalente a verificar que el usuario sea superadmin del sistema.
    """
    message = "Acceso denegado. Se requiere permiso 'root'."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return (
            request.user.role is not None
            and request.user.role.permission == 'root'
        )


class CanAccessSimpleResources(permissions.BasePermission):
    """
    Permiso para usuarios con permission='simple' o permission='root'.
    Permite acceso a recursos de Tareas e Imagenes.
    """
    message = "Acceso denegado. Se requiere permiso 'simple' o 'root'."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if request.user.role is None:
            return False

        perm = request.user.role.permission
        return perm in ('root', 'simple', 'user')


class IsOwner(permissions.BasePermission):
    """
    Permiso a nivel de objeto que solo permite acceso al propietario del recurso.
    Un usuario con permission='root' tiene acceso total.
    """
    message = "No tienes permiso para acceder a este recurso. Solo el propietario puede hacerlo."

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if request.user.role and request.user.role.permission == 'root':
            return True

        return hasattr(obj, 'user') and obj.user == request.user
