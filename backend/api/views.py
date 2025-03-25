from rest_framework import viewsets

from . import models, serializers


class RecipeViewSet(viewsets.GenericViewSet):
    '''
    Получение списка рецептов.
    '''
    queryset = models.Recipe.objects.all()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Получение списка тэгов.
    Создание и редактирование только в админке.
    '''
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Получение списка ингредиентов.
    Создание и редактирование только в админке.
    '''
    queryset = models.Ingredient.objects.all()
