from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.fields import SerializerMethodField

from . import models as models


class CustomUserSerializer(UserSerializer):
    '''
    Сериализатор для кастомного пользователя.
    '''

    is_subscribed = SerializerMethodField()

    class Meta:
        model = models.CustomUser
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор для создания кастомного пользователя.
    """

    class Meta:
        model = models.CustomUser
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
        )
