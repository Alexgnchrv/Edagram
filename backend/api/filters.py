import django_filters
from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class RecipeFilter(filters.FilterSet):
    """Фильтр для модели Recipe."""
    is_favorited = filters.CharFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.CharFilter(
        method='filter_is_in_shopping_cart')
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'tags', 'author',)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value == '1' and user.is_authenticated:
            return queryset.filter(recipes_favourite_recipe_related__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value == '1' and user.is_authenticated:
            return queryset.filter(
                recipes_shoppingcart_recipe_related__user=user)
        return queryset


class IngredientFilter(django_filters.FilterSet):
    """Фильтр для ингредиентов."""
    name = django_filters.CharFilter(
        lookup_expr='istartswith',
        label='Название ингредиента'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
