from djoser.views import UserViewSet

from . import models, serializers


class CustomUserViewSet(UserViewSet):
    '''
    Кастомное представление для пользователей.
    '''

    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer
