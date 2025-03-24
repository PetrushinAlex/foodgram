from rest_framework import serializers

from . import models as mod


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для создания/обновления рецепта (на основе модели рецепта).
    '''

    class Meta:
        model = mod.Recipe


class TagSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для тэгов на основе соответствующей модели.
    '''

    class Meta:
        model = mod.Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для ингридиентов на основе соответствующей модели.
    '''

    class Meta:
        model = mod.Ingredient
        fields = '__all__'
