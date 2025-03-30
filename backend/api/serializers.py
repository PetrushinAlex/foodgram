from django.contrib.auth import get_user_model
from rest_framework import relations, serializers
from drf_extra_fields.fields import Base64ImageField

from ..food import models


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
