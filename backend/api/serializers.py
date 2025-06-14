from django.contrib.auth import get_user_model
from rest_framework import relations, serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.fields import SerializerMethodField

from food import models
from tools import constants


User = get_user_model()


class UserSerializer(UserSerializer):
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


class UserCreateSerializer(UserCreateSerializer):
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


class SubscribeSerializer(UserSerializer):
    '''
    Сериализатор на основе сериализатора кастомного пользователя
    с информацией о подписках.
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
            recipes_limit_value = recipes_limit or constants.DEFAULT_PAGE_SIZE
            recipes = obj.author.recipes.all()[:recipes_limit_value]

            return RecipeListSerializer(
                recipes,
                many=True,
                context=self.context
            ).data


class TagSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для тэгов на основе соответствующей модели.
    '''
    class Meta:
        model = models.Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для ингридиентов на основе соответствующей модели.
    '''
    class Meta:
        model = models.Ingredient
        fields = (
            'id', 
            'name',
            'measurement_unit',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для ингридиентов под рецепты.
    '''
    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = models.RecipeIngredient
        fields = (
            'id', 
            'name',
            'amount',
            'measurement_unit',
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для создания ингредиентов в рецептах.
    '''
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = models.Ingredient
        fields = (
            'id',
            'amount',
            'measurement_unit',
        )


class RecipeSimpleSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для упрощенного представления рецептов.
    '''
    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'name',
            'cooking_time',
            'image',
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для создания/обновления рецепта (на основе модели рецепта).
    '''
    image = Base64ImageField()
    tags = relations.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Tag.objects.all(),
    )
    ingredients = RecipeIngredientCreateSerializer(
        many=True,
    )
    author = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'name',
            'author',
            'image',
            'tags',
            'ingredients',
            'text',
            'cooking_time',
        )
    
    def validate_tags(self, tags):
        '''
        Валидация добавления тэгов 
        (должен быть добавлен хотя бы один).
        '''
        if not tags:
            raise ValidationError(
                'Добавьте хотя бы один тэг!'
            )
        return tags
    
    def validate_ingredients(self, ingredients):
        '''
        Валидация добавления ингредиентов
        (ингредиенты не должны повторяться,
        также должен быть указан хотя бы один).
        '''
        ingredients_array = [ingr['id'] for ingr in ingredients]
        if len(set(ingredients_array)) != len(ingredients_array):
            raise ValidationError(
                'Не указывайте один и тот же ингредиент дважды.'
            )
        if not ingredients:
            raise ValidationError(
                'Добавьте хотя бы один ингредиент!'
            )
        return ingredients
    
    def add_ingredients(self, recipe, ingredients):
        '''
        Метод добавления ингредиентов. Используется bulk_create
        для избежания отдельных запросов для каждого объекта.
        '''
        models.RecipeIngredient.objects.bulk_create(
            [
                models.RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient.get('id'),
                    amount=ingredient.get('amount'),
                )
                for ingredient in ingredients
            ]
        )
    
    def create(self, validated_data):
        '''
        Метод создания рецепта с добавлением
        ингредиентов с помощью метода add_ingredients.
        '''
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = models.Recipe.objects.create(
            author=author,
            **validated_data,
        )
        recipe.tags.set(tags)
        self.add_ingredients(
            recipe=recipe,
            ingredients=ingredients,
        )
        return recipe
    

    def update(self, instance, validated_data):
        '''
        Метод для обновления рецепта так же используя
        метод add_ingredients для ингредиентов.
        '''
        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.add_ingredients(
                recipe=instance,
                ingredients=ingredients,
            )
        return super().update(instance, validated_data)

    

class RecipeListSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для получения списка рецептов.
    '''
    author = UserSerializer(
        read_only=True,
    )
    image = serializers.ReadOnlyField(
        source='image.url',
    )
    tags = TagSerializer(
        many=True,
    )
    ingredients = IngredientSerializer(
        many=True,
        source='recipe_ingredients',
        required=True,
    )
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_in_favorite = serializers.SerializerMethodField()

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'name',
            'author',
            'image',
            'tags',
            'ingredients',
            'text',
            'cooking_time',
        )
    
    def get_is_in_shopping_cart(self, obj):
        '''
        Метод, позволяющий получить информацию о рецепте
        в корзине пользователя.
        Проверяет, анонимен ли пользователь.
        '''
        user = self.context.get('request').user
        if not user.is_anonymous:
            return user.shopping_cart.filter(
                recipe=obj
            ).exists()
        return False
    
    def get_is_in_favorite(self, obj):
        '''
        Метод, позволяющий получить информацию о рецепте
        в избранном у пользователя.
        Проверяет, анонимен ли пользователь.
        '''
        user = self.context.get('request').user
        if not user.is_anonymous:
            return user.favorite.filter(
                recipe=obj
            ).exists()
        return False
