from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from . import serializers
from food import models
from tools import filters, paginators


class RecipeViewSet(viewsets.GenericViewSet):
    '''
    Получение списка рецептов, добавление, апдейт и удаление рецептов.
    '''
    queryset = models.Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.RecipeFilter
    pagination_class = paginators.CustomRecipePaginator

    def add_to(self, model, user, pk):
        '''
        Метод для добавления рецепта в модель.
        '''
        pass

    def delete_from(self, model, user, pk):
        '''
        Метод для удаления рецепта из модели.
        '''
        pass

    def get_permission(self):
        pass


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
