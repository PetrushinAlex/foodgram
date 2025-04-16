from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from . import serializers
from food import models
from tools import filters


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
    serializer_class = serializers.IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.IngredientFilter
