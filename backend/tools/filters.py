from django_filters.rest_framework import FilterSet, filters
from food import models


class RecipeFilter(FilterSet):
    '''
    Фильтр для рецептов с возможностью фильтрации по:
    - автору
    - тегам
    - наличию в списке покупок
    - наличию в избранном
    '''

    author = filters.CharFilter(
        field_name='author__id',
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=models.Tag.objects.all(),
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_shopping_cart_recipes',
    )
    is_favorited = filters.BooleanFilter(
        method='filter_favorite_recipes',
    )

    class Meta:
        model = models.Recipe
        fields = (
            'author',
            'tags',
            'is_in_shopping_cart',
            'is_favorited',
        )

    def filter_shopping_cart_recipes(self, queryset, name, value):
        '''
        Фильтрует рецепты по их наличию в списке покупок пользователя.
        '''

        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(shopping_cart__user=user)
        return queryset

    def filter_favorite_recipes(self, queryset, name, value):
        '''
        Фильтрует рецепты по их наличию в избранном пользователя.
        '''

        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(favorite__user=user)
        return queryset


class IngredientSearchFilter(FilterSet):
    '''
    Фильтр для поиска ингредиентов по названию.
    Поддерживает поиск по начальным буквам (case-insensitive).
    '''

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = models.Ingredient
        fields = ('name',)
