from rest_framework import serializers

from . import models


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для создания/обновления рецепта (на основе модели рецепта).
    '''

    class Meta:
        model = models.Recipe


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
