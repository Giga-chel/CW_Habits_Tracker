from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Доступ к объекту только его владельцу."""

    message = "Вы не являетесь владельцем этой привычки."

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
