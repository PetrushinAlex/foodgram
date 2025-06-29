from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import relations, serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from djoser.serializers import (
    UserSerializer as DjoserUserSerializer,
)
from rest_framework.fields import SerializerMethodField

from food.models import (
    Recipe, Tag, Ingredient, Favorite, ShoppingCart, RecipeIngredient
)
from users.models import Sub
from tools import constants


User = get_user_model()


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    '''
    Преобразует данные о избранных рецептах.
    Возвращает сокращенную информацию о рецепте.
    '''

    class Meta:
        model = Recipe
        fields = ('id',)

    def to_representation(self, instance):
        '''
        Преобразует ID рецепта в полные данные о нем.
        '''

        representation = super().to_representation(instance)
        favorite = get_object_or_404(
            Favorite, 
            pk=representation['id'],
        )
        return RecipeSimpleSerializer(favorite.recipe).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    '''
    Обрабатывает операции с корзиной покупок.
    Управляет добавлением и удалением рецептов.
    '''

    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']
        read_only_fields = ['user']

    def validate(self, data):
        '''
        Проверяет, что рецепт еще не добавлен в корзину.
        '''

        request = self.context['request']

        recipe = data['recipe']

        if request.user.shopping_cart.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен'
            )
        return data

    def to_representation(self, instance):
        '''
        Возвращает упрощенные данные о рецепте.
        '''

        return RecipeSimpleSerializer(instance.recipe).data


class UserSerializer(DjoserUserSerializer):
    '''
    Расширенный сериализатор пользователей.
    Добавляет информацию о подписках и аватаре.
    '''

    is_subscribed = SerializerMethodField()
    avatar = Base64ImageField(
        required=False,
        allow_null=True,
    )

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
        read_only_fields = (
            'id',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        '''
        Определяет, подписан ли текущий пользователь на этого автора.
        '''

        request = self.context.get('request')
        user = request.user
        if request and user.is_authenticated and user.subscriptions.filter(
            author=obj
        ).exists():
            return True
        return False


class SubscribeSerializer(serializers.ModelSerializer):
    '''
    Формирует данные о подписках пользователя.
    Включает количество рецептов и их сокращенный список.
    '''

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')
    is_subscribed = SerializerMethodField()
    avatar = Base64ImageField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count'
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        '''
        Проверяет наличие активной подписки.
        '''

        request = self.context.get('request')
        user = request.user
        if request and user.is_authenticated and user.subscriptions.filter(
            author=obj
        ).exists():
            return True
        return False

    def get_recipes(self, obj):
        '''
        Возвращает ограниченное количество рецептов автора.
        Поддерживает параметр recipes_limit для ограничения вывода.
        '''

        request = self.context.get('request')
        recipes = obj.recipes.all()

        try:
            limit = int(request.GET.get('recipes_limit'))
            recipes = recipes[:limit]
        except (ValueError, TypeError):
            pass

        return RecipeSimpleSerializer(
            recipes, many=True, context=self.context
        ).data


class TagSerializer(serializers.ModelSerializer):
    '''
    Преобразует данные о кулинарных тегах.
    '''

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    '''
    Обрабатывает информацию об ингредиентах.
    Включает единицы измерения для каждого ингредиента.
    '''

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    '''
    Связывает рецепты с ингредиентами.
    Указывает количество ингредиентов для каждого рецепта.
    '''

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id',
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True,
    )
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSimpleSerializer(serializers.ModelSerializer):
    '''
    Сокращенная версия данных о рецепте.
    Используется для вложенных представлений.
    '''

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'cooking_time',
            'image',
        )
        read_only_fields = (
            'id',
            'name',
            'cooking_time',
            'image',
        )


class RecipeSerializer(serializers.ModelSerializer):
    '''
    Основной сериализатор рецептов.
    Обеспечивает полный цикл работы с рецептами.
    '''

    author = UserSerializer(
        read_only=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients',
    )
    image = Base64ImageField(
        required=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(
        min_value=1,
        max_value=9999,
        validators=[
            MinValueValidator(
                1,
                message=f'Время приготовления не '
                        f'может быть меньше {1} минуты',
            ),
            MaxValueValidator(
                9999,
                message=f'Время приготовления не '
                        f'может превышать {9999} минут',
            ),
        ],
    )

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        ]

    def validate(self, data):
        '''
        Комплексная проверка данных рецепта.
        Контролирует теги, ингредиенты, время приготовления и изображение.
        '''

        t = data.get('tags', [])
        ingredients = data.get('recipe_ingredients', [])
        image = data.get('image')
        cooking_time = data.get('cooking_time')

        if self.context['request'].method == 'POST' and (
                image is None or image == ''):
            raise serializers.ValidationError(
                {'image':
                     'Изображение не заполненно'
                 }
            )

        if not t:
            raise serializers.ValidationError(
                {'tags':
                     'Поле Тег  не заполненно'
                 }
            )
        t_ids = [tag.id for tag in t]
        if len(t_ids) != len(set(t_ids)):
            raise serializers.ValidationError(
                {'tags':
                     'Дублирование тегов!.'
                 }
            )

        if not ingredients:
            raise serializers.ValidationError(
                {'ingredient':
                     'Поле Ингридиент  не заполненно'
                     ''
                }
            )
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            if amount is None:
                raise serializers.ValidationError(
                    {
                        'amount': 'Нет количества'
                    }
                )
            if not (1 <= amount <= 9999):
                raise serializers.ValidationError(
                    {
                        'amount': f'Кол-во должно быть между {1} и {9999}.'
                    }
                )

        if len(ingredients) != len(
                {i['ingredient']['id'] for i in ingredients}
        ):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не должны повторяться.'}
            )
        if cooking_time is None:
            raise serializers.ValidationError(
                {'cooking_time': 'Время приготовления обязательно.'}
            )
        if not (1 <= cooking_time <= 9999):
            raise serializers.ValidationError(
                {
                    'cooking_time': f'Время должно быть {1} - {9999} мин.'
                }
            )
        if image is None or image == '':
            raise serializers.ValidationError(
                {'image': 'Изображение  не заполненно'}
            )

        return data

    def get_is_favorited(self, obj):
        '''
        Проверяет, находится ли рецепт в избранном.
        '''

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorite.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        '''
        Определяет, добавлен ли рецепт в корзину.
        '''

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.shopping_cart.filter(
                user=request.user
            ).exists()
        return False

    def create(self, validated_data):
        '''
        Создает новый рецепт с указанными тегами и ингредиентами.
        '''

        i_data = validated_data.pop('recipe_ingredients', [])
        t_data = validated_data.pop('tags', [])

        validated_data.pop('author', None)

        author = self.context['request'].user

        recipe = Recipe.objects.create(author=author, **validated_data)

        recipe.tags.set(t_data)
        self.ing_up_and_cr(recipe, i_data)

        return recipe

    def ing_up_and_cr(self, recipe, ingredients_data):
        '''
        Внутренний метод для обработки ингредиентов.
        Создает связи между рецептом и ингредиентами.
        '''

        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient_data['ingredient']['id'].id,
                amount=ingredient_data['amount'],
            )
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return recipe_ingredients

    def update(self, instance, validated_data):
        '''
        Обновляет существующий рецепт.
        Полностью заменяет теги и ингредиенты.
        '''

        if 'image' not in validated_data:
            validated_data['image'] = instance.image

        i_data = validated_data.pop(
            'recipe_ingredients',
            []
        )
        t_data = validated_data.pop('tags', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.tags.set(t_data)
        instance.recipe_ingredients.all().delete()
        self.ing_up_and_cr(instance, i_data)
        return instance

    def to_representation(self, instance):
        '''
        Формирует итоговое представление рецепта.
        Добавляет полные данные о тегах.
        '''

        rep = super().to_representation(instance)
        rep['tags'] = TagSerializer(
            instance.tags.all(),
            many=True
        ).data
        return rep


class AvatarSerializer(serializers.Serializer):
    '''
    Обрабатывает загрузку аватара пользователя.
    '''
    avatar = Base64ImageField(required=True)
