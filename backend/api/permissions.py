from rest_framework.permissions import IsAuthenticated, SAFE_METHODS


class IsAuthorOrReadOnlyPermission(IsAuthenticated):
    """
    Разрешение, позволяющее:
    - Чтение (GET, HEAD, OPTIONS) для всех пользователей
    - Запись только автору объекта
    - Только аутентифицированным пользователям для небезопасных методов
    """

    def has_permission(self, request, view):
        """
        Проверка базовых разрешений для эндпоинта
        """

        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """
        Проверка разрешений для конкретного экземпляра объекта
        """

        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )
