from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from . import serializers
from food import models
from tools import filters, paginators, permissions


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
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {"Ошибка": "Рецепт уже был добавлен"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe = get_object_or_404(
            models.Recipe, 
            id=pk,
        )
        model.objects.create(
            user=user, 
            recipe=recipe,
        )
        serializer = serializers.RecipeCreateUpdateSerializer(recipe)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED,
        )

    def delete_from(self, model, user, pk):
        '''
        Метод для удаления рецепта из модели.
        '''
        pass

    def get_permissions(self):
        '''
        Переопределяет пермишен для создания, апдейта 
        и удаления рецепта.
        '''
        if self.action is 'create':
            return (IsAuthenticated(),)
        if self.action in ('destroy', 'update',):
            return (permissions.IsAuthorOrAdmin(),)
        return super().get_permissions()
    
    def get_serializer_class(self):
        '''
        Переопределяет метод сериализации, разделяя ее
        на "безопасные" методы и остальные.
        '''
        serializer_class = (
            serializers.RecipeListSerializer
            if self.request.method in SAFE_METHODS
            else serializers.RecipeCreateUpdateSerializer
        )
        return serializer_class


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
