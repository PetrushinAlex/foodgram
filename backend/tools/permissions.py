from rest_framework import permissions


class IsAuthorOrAdmin(permissions.BasePermission):
    '''
    Переопределенный пермишен для проверки аутентификации
    пользователя в роли администратора или автора.
    '''
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            or request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_superuser
            or obj.author == request.user
        )
