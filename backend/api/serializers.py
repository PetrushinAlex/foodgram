from django.contrib.auth import get_user_model
from rest_framework import relations, serializers
from drf_extra_fields.fields import Base64ImageField

from food import models


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для тэгов на основе соответствующей модели.
    '''

    class Meta:
        model = models.Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для ингридиентов на основе соответствующей модели.
    '''

    class Meta:
        model = models.Ingredient
        fields = '__all__'


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для создания/обновления рецепта (на основе модели рецепта).
    '''

    image = Base64ImageField()
    tags = relations.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(),
        many=True,
    )

    class Meta:
        model = models.Recipe
    

class RecipeListSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для получения списка рецептов.
    '''

    author = ...
    image = serializers.ReadOnlyField(
        source='image.url',
    )
    tags = TagSerializer(
        many=True,
    )
    ingredients = IngredientSerializer(
        many=True,
    )

    class Meta:
        model = models.Recipe
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для ингридиентов под рецепты.
    '''

    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.id',
    )

    class Meta:
        model = models.RecipeIngredient
        fields = '__all__'


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для создания ингредиентов в рецептах.
    '''

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = models.Ingredient
        fields = ('id', 'amount',)
