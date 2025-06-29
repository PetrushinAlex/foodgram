from io import BytesIO
from django.db.models import Sum
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from docx import Document
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models.functions import Lower
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.response import Response
from rest_framework import permissions

from . import serializers as myserializers
from food.models import (
    Recipe, Tag, Ingredient, Favorite, ShoppingCart, RecipeIngredient
)
from users.models import Sub
from tools import (
    filters as tools_filters,
    paginators as tools_paginators,
    permissions as tools_permissions
)


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    '''
    Кастомное представление для пользователей.
    '''

    pagination_class = tools_paginators.Paginator

    def get_serializer_class(self):

        if self.action == 'list':
            return myserializers.UserSerializer
        elif self.action == 'retrieve':
            return myserializers.UserSerializer
        return super().get_serializer_class()

    def get_permissions(self):

        if self.action == 'list':
            return [permissions.AllowAny()]
        elif self.action == 'retrieve':
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(
        methods=['get'],
        detail=False,
        url_path='me',
        permission_classes=[IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):

        serializer = myserializers.UserSerializer(
            request.user,
            context={'request': request}
        )
        date_of_serializer = serializer.data
        return Response(date_of_serializer)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request, *args, **kwargs):

        if request.method == 'DELETE':
            if request.user.avatar:
                if default_storage.exists(request.user.avatar.name):
                    default_storage.delete(request.user.avatar.name)
                request.user.avatar = None
                request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = myserializers.AvatarSerializer(
                data=request.data
            )
            serializer.is_valid(raise_exception=True)
            request.user.avatar = serializer.validated_data['avatar']
            request.user.save()

            response_data = {'avatar': request.user.avatar.url}
            return Response(
                response_data,
                status=status.HTTP_200_OK,
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='subscribe',
    )
    def subscribe(self, request, *args, **kwargs):

        author = self.get_object()
        user = request.user
        if request.method == 'POST':
            return self._create_subscription(user, author, request)
        return self._delete_subscription(user, author)

    def _create_subscription(self, user, author, request):
        '''
        Создает подписку на пользователя
        '''

        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        _, created = Sub.objects.get_or_create(
            user=user, author=author
        )
        if not created:
            return Response(
                {'errors': f'Вы уже подписаны на {author.username}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = myserializers.SubscribeSerializer(
            author, context={'request': request}
        ).data
        return Response(data, status=status.HTTP_201_CREATED)

    def _delete_subscription(self, user, author):
        '''
        Удаляет подписку на пользователя.
        '''

        subscription = Sub.objects.filter(
            user=user, author=author
        ).first()
        if not subscription:
            return Response(
                {'errors': 'Подписка не найдена.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='subscriptions',
    )
    def subscriptions(self, request, *args, **kwargs):

        user = request.user
        queryset = User.objects.filter(users_subscribers__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = myserializers.SubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all()
    serializer_class = myserializers.RecipeSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        tools_permissions.IsAuthorOrReadOnlyPermission,
    ]
    pagination_class = tools_paginators.Paginator
    filter_backends = [DjangoFilterBackend]
    filterset_class = tools_filters.RecipeFilter

    def perform_create(self, serializer):
        '''
        Автоматически устанавливает автора при создании рецепта.
        '''

        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def link(self, request, pk=None):
        '''
        Генерирует короткую ссылку на рецепт.
        Возвращает URL для перенаправления к рецепту.
        '''

        get_object_or_404(Recipe, id=pk)
        short_url = request.build_absolute_uri(
            reverse('redirect_recipe', kwargs={'pk': pk})
        )
        return Response({'short-link': short_url})

    @action(
        detail=True,
        methods=['post'],
        url_name='shopping_cart',
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        '''
        Добавляет рецепт в список покупок текущего пользователя.
        '''

        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        cart_relation, created = ShoppingCart.objects.get_or_create(
            user=user, recipe=recipe)

        if not created:
            return Response(
                {'errors': f"Рецепт '{recipe.name}' уже в списке покупок"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = myserializers.RecipeSimpleSerializer(
            recipe, context={'request': request})
        return Response(
            serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        '''
        Удаляет рецепт из списка покупок текущего пользователя.
        '''

        recipe = get_object_or_404(Recipe, pk=pk)
        cart_relation = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe)

        if not cart_relation.exists():
            return Response(
                {'errors': 'Рецепт не найден в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        url_name='favorite',
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        '''
        Добавляет рецепт в избранное для текущего пользователя.
        '''

        recipe = get_object_or_404(Recipe, id=pk)

        user = request.user

        favorite_relation, created = Favorite.objects.get_or_create(
            user=user, recipe=recipe)

        if not created:
            return Response(
                {'errors': f"Рецепт '{recipe.name}' уже в избранном"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = myserializers.RecipeSimpleSerializer(
            recipe, context={'request': request})
        return Response(
            serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def remove_from_favorite(self, request, pk=None):
        '''
        Удаляет рецепт из избранного текущего пользователя.
        '''

        recipe = get_object_or_404(Recipe, pk=pk)
        favorite_relation = Favorite.objects.filter(
            user=request.user, recipe=recipe)

        if not favorite_relation.exists():

            return Response(
                {'errors': 'Рецепт не найден в избранном'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        favorite_relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):

        document = Document()
        document.add_heading('Список покупок', level=1)
        recipes_shop = request.user.shopping_cart
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__in=recipes_shop.values_list('recipe', flat=True)
            )
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        if ingredients:
            table = document.add_table(rows=1, cols=3)
            table.style = 'Table Grid'
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = '№'
            hdr_cells[1].text = 'Ингредиент'
            hdr_cells[2].text = 'Количество'

            for idx, ing in enumerate(ingredients, start=1):
                row_cells = table.add_row().cells
                row_cells[0].text = str(idx)
                row_cells[1].text = ing['ingredient__name']
                row_cells[2].text = (
                    f"{ing['total_amount']} "
                    f"{ing['ingredient__measurement_unit']}"
                )
        else:
            document.add_paragraph('Список покупок пуст!')

        buffer = BytesIO()
        document.save(buffer)
        buffer.seek(0)

        сontent_type = (
            'application/vnd.openxmlformats-officedocument.'
            'wordprocessingml.document'
        )
        return FileResponse(
            buffer,
            as_attachment=True,
            filename='shopping_list.docx',
            content_type=сontent_type,
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Получение списка тэгов.
    Создание и редактирование только в админке.
    '''

    queryset = Tag.objects.all()
    serializer_class = myserializers.TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Получение списка ингредиентов.
    Создание и редактирование только в админке.
    '''

    queryset = Ingredient.objects.all().order_by(Lower('name'))
    serializer_class = myserializers.IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = tools_filters.IngredientSearchFilter
    pagination_class = None
