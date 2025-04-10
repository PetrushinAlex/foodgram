from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from api import serializers as srls


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    '''
    Сериализатор для кастомного пользователя с дополнительной
    информацией (о подписке).
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

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.subscriber.filter(author=obj).exists()


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

        def get_is_subscribed(self, obj):
            user = self.context['request'].user
            return (
                user.is_authenticated
                and user.subscriber.filter(author=obj.author).exists()
            )
        
        def get_recipes(self, obj):
            request = self.context.get('request')
            recipes_limit = request.query_params.get('recipes_limit')
            if recipes_limit is not None:
                try:
                    recipes_limit = int(recipes_limit)
                except ValueError:
                    recipes_limit = None
            recipes_limit_value = recipes_limit or settings.DEFAULT_PAGE_SIZE
            recipes = obj.author.recipes.all()[:recipes_limit_value]

            return srls.RecipeListSerializer(
                recipes,
                many=True,
                context=self.context
            ).data
