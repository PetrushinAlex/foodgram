from django_filters.rest_framework import FilterSet, filters

from food import models


class RecipeFilter(FilterSet):
    '''
    Фильтр для вьюсета рецептов.
    '''
    author = filters.CharFilter(
        field_name='author__id',
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=models.Tag.objects.all(),
    )
    is_in_shoppin_cart = filters.BooleanFilter(
        method='filter_is_in_shoppin_cart',
    )
    is_in_favorite = filters.BooleanFilter(
        method='filter_is_in_favorite',
    )

    class Meta:
        model = models.Recipe
        fields = (
            'author',
            'tags',
            'is_in_shoppin_cart',
            'is_in_favorite',
        )
    
    def filter_is_in_shoppin_cart(self, queryset, name, value):
        '''
        Метод для фильтрации рецептов по нахождению их в 
        корзине для покупок у запрашиваемого пользователя.
        '''
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(shopping_cart__user=user)
        return queryset

    def filter_is_in_favorite(self, queryset, name, value):
        '''
        Метод для фильтрации рецептов по нахождению их в
        избранном у запрашиваемого пользователя.
        '''
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(favorite__user=user)
        return queryset


class IngredientFilter(FilterSet):
    '''
    Фильтр для вьюсета ингредиентов.
    '''
    name = filters.CharFilter(
        lookup_expr='startswith',
    )

    class Meta:
        model = models.Ingredient
        fields = (
            'name',
        )
