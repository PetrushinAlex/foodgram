from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    '''
    Сериализатор для кастомного пользователя.
    '''

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
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
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
        )


class SubSerializer(CustomUserSerializer):
    '''
    Сериализатор на основе сериализатора кастомного пользователя
    с информацией про подписки.
    '''

    recipes = serializers.SerializerMethodField()
    recipe_quantity = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipe_quantity',
        )
        read_only_fields = (
            'username',
            'email',
            'first_name',
            'last_name',
        )
