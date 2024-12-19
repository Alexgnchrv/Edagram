import logging

import django_filters

from recipes.models import Ingredient

logger = logging.getLogger('filter_logger')


class IngredientFilter(django_filters.FilterSet):
    """Фильтр для ингредиентов."""
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Название ингредиента'
    )

    class Meta:
        model = Ingredient
        fields = ['name']
