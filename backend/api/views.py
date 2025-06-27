from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.storage import default_storage
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)

from . import serializers as myserializers
from food import models
from tools import filters, paginators, permissions


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    '''
    Кастомное представление для пользователей.
    '''

    pagination_class = paginators.Paginator


    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return myserializers.UserSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=['get'],
        url_path='me',
        permission_classes=[IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        serializer = myserializers.UserSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request, *args, **kwargs):
        user = request.user

        if request.method == 'DELETE':
            if user.avatar:
                if default_storage.exists(user.avatar.name):
                    default_storage.delete(user.avatar.name)
                user.avatar = None
                user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = myserializers.AvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        avatar = serializer.validated_data['avatar']
        user.avatar = avatar
        user.save()
        return Response(
            {'avatar': user.avatar.url}, status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(
            User,
            id=self.kwargs.get('id'),
        )

        if request.method == 'POST':
            serializer = myserializers.SubscribeSerializer(
                author,
                data=request.data,
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            models.Sub.objects.create(
                user=user,
                author=author,
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        subscription = get_object_or_404(
            models.Sub, 
            user=user, 
            author=author,
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            subscription__user=request.user,
        )
        pages = self.paginate_queryset(queryset)
        serializer = myserializers.SubscribeSerializer(
            pages, 
            many=True, 
            context={"request": request},
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.GenericViewSet):
    '''
    Получение списка рецептов, добавление, апдейт и удаление рецептов.
    '''
    queryset = models.Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.RecipeFilter
    pagination_class = paginators.CustomRecipePaginator

    def add_recipe_to(self, model, user, pk):
        '''
        Метод для добавления рецепта в определенную модель.
        '''
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'Ошибка': 'Рецепт уже добавлен'},
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
        serializer = myserializers.RecipeSimpleSerializer(recipe)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED,
        )

    def remove_recipe_from(self, model, user, pk):
        '''
        Метод для удаления рецепта из определенной модели.
        '''
        obj = model.objects.filter(
            recipe__id=pk,
            user=user,
        )
        if obj.exists():
            obj.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {'Ошибка':'Рецепт уже удален или не существует'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        '''
        Добавляет или удаляет рецепт из корзины покупок 
        пользователя, используя ранее определенные методы.
        '''
        if request.method == 'POST':
            return self.add_recipe_to(
                models.ShoppingCart,
                request.user,
                pk
            )
        return self.remove_recipe_from(
            models.ShoppingCart,
            request.user,
            pk
        )

    def download_shopping_cart(self, request):
        '''
        Скачать список ингредиентов из списка покупок 
        пользователя из запросов.
        '''
        user = request.user
        if user.shopping_cart.exists() == False:
            return Response(
                {'Ошибка':'Корзина не заполнена'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ingredients = (
            models.RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=user
            )
            .values(
                'ingredient__name', 
                'ingredient__measurement_unit',
            )
            .order_by('ingredient__name')
            .annotate(amount=Sum('amount'))
        )
        shopping_cart = f'Корзина {user}\n'
        for ingr in ingredients:
            shopping_cart += (
                f'{ingr["ingredient__name"].capitalize()},'
                f'{ingr["amount"]}'
                f'{ingr["ingredient__measurement_unit"]}'
            )
        file_name = f'shopping_cart_of_{user}.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file_name}'

        return response
    
    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        '''
        Добавляет или удаляет рецепт из избранного у 
        пользователя, используя ранее определенные методы.
        '''
        if request.method == 'POST':
            return self.add_recipe_to(
                models.Favorite,
                request.user,
                pk
            )
        if request.method == 'DELETE':
            return self.remove_recipe_from(
                models.Favorite,
                request.user,
                pk
            )

    def get_permissions(self):
        '''
        Переопределяет пермишен для создания, апдейта 
        и удаления рецепта (create, update, destroy).
        '''
        if self.action == 'create':
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
            myserializers.RecipeListSerializer
            if self.request.method in SAFE_METHODS
            else myserializers.RecipeCreateUpdateSerializer
        )
        return serializer_class


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Получение списка тэгов.
    Создание и редактирование только в админке.
    '''
    queryset = models.Tag.objects.all()
    serializer_class = myserializers.TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Получение списка ингредиентов.
    Создание и редактирование только в админке.
    '''
    queryset = models.Ingredient.objects.all()
    serializer_class = myserializers.IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.IngredientFilter
