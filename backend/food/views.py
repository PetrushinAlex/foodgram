from food.models import Recipe

from django.shortcuts import get_object_or_404, redirect


def redirect_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return redirect(f'recipes/{recipe.pk}/')
