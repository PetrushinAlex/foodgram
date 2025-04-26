from django.contrib.auth import get_user_model
from rest_framework import relations, serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError

from food import models
from users import serializers as userserializers


User = get_user_model()


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
    author = userserializers.CustomUserSerializer(
        many=True,
    )

    class Meta:
        model = models.Recipe
        fields = '__all__'
    
    def validate_tags(self, tags):
        '''
        Валидация добавления тэгов 
        (должен быть добавлен хотя бы один).
        '''
        if not tags:
            raise ValidationError(
                'Добавьте тэг!'
            )
        return tags
    
    def validate_ingredients(self, ingredients):
        '''
        Валидация добавления ингредиентов
        (ингредиенты не должны повторяться,
        также должен быть указан хотя бы один).
        '''
        if not ingredients:
            raise ValidationError(
                'Добавьте хотя бы один ингредиент!'
            )
        ingredients_array = [ingr['id'] for ingr in ingredients]
        if len(set(ingredients_array)) != len(ingredients_array):
            raise ValidationError(
                'Не указывайте один и тот же ингредиент дважды.'
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
        return super().update(instance, validated_data,)

    

class RecipeListSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для получения списка рецептов.
    '''
    author = userserializers.CustomUserSerializer(
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
        user = self.context.get('request').user
        if not user.is_anonymous:
            return user.shopping_cart.filter(
                recipe=obj
            ).exists()
        return False
    
    def get_is_in_favorite(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return user.favorite.filter(
                recipe=obj
            ).exists()
        return False
