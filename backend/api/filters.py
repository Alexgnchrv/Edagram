import django_filters
from django_filters.rest_framework import FilterSet

from recipes.models import Ingredient, Recipe, Tag


class RecipeQueryFilter(FilterSet):
    """Фильтр для рецептов."""

    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        label='Теги',
        field_name='tags__slug',
        to_field_name='slug',
    )

    is_favourite = django_filters.BooleanFilter(
        field_name='favourited_by',
        method='filter_favourite',
        label='В избранном'
    )

    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name='in_shopping_cart',
        method='filter_in_shopping_cart',
        label='В корзине'
    )

    class Meta:
        model = Recipe
        fields = ['tags']

    def filter_favourite(self, queryset, name, value):
        """Фильтрация по избранному рецепту."""

        if value:
            return queryset.filter(
                favourited_by__user=self.request.user
            )
        return queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        """Фильтрация по рецепту, добавленному в корзину."""

        if value:
            return queryset.filter(
                in_shopping_cart__user=self.request.user
            )
        return queryset


class IngredientFilter(django_filters.FilterSet):
    """Фильтр для ингредиентов."""
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Название ингредиента'
    )

    class Meta:
        model = Ingredient
        fields = ['name']
