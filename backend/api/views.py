from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Favourite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, ShortURL, Tag)

from .filters import IngredientFilter, RecipeFilter
from .pagination import StandardPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (AddToModelSerializer, CompactRecipeSerializer,
                          IngredientSerializer, RecipeCreationSerializer,
                          RecipeDetailSerializer, TagSerializer)


@require_GET
def short_url_redirect(request, short_code):
    try:
        short_url = ShortURL.objects.get(short_code=short_code)
        return redirect(f'/recipes/{short_url.recipe.pk}/')
    except ShortURL.DoesNotExist:
        raise Http404('Короткая ссылка не найдена.')


class RecipeViewSet(ModelViewSet):
    """ViewSet для рецептов."""

    queryset = Recipe.objects.all()
    pagination_class = StandardPagination
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_url, created = ShortURL.objects.get_or_create(recipe=recipe)
        short_url_path = reverse('short-url-redirect',
                                 kwargs={'short_code': short_url.short_code})
        short_link = request.build_absolute_uri(short_url_path)

        return Response({
            'short-link': short_link
        }, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """Метод для сохранения рецепта с текущим пользователем как автором."""

        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Метод для выбора сериализатора в зависимости от действия."""

        if self.request.method in SAFE_METHODS:
            return RecipeDetailSerializer
        return RecipeCreationSerializer

    def add_to_model(self, request, pk, model):
        """Добавление рецепта в модель (избранное или корзина)."""

        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = AddToModelSerializer(
            data={'user': request.user.id, 'recipe': pk},
            model=model
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CompactRecipeSerializer(recipe).data,
                        status=status.HTTP_201_CREATED)

    def remove_from_model(self, request, pk, model):
        """Удаление рецепта из модели (избранное или корзина)."""

        recipe = get_object_or_404(Recipe, id=pk)
        obj = model.objects.filter(user=request.user, recipe=recipe).first()
        if not obj:
            return Response({'detail': 'Запись не найдена для удаления.'},
                            status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.add_to_model(request, pk, Favourite)

    @favorite.mapping.delete
    def remove_favorite(self, request, pk):
        return self.remove_from_model(request, pk, Favourite)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.add_to_model(request, pk, ShoppingCart)

    @shopping_cart.mapping.delete
    def remove_from_cart(self, request, pk):
        return self.remove_from_model(request, pk, ShoppingCart)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Метод для скачивания списка покупок."""

        user = request.user

        if not user.recipes_shoppingcart_user_related.exists():
            return Response(
                {'error': 'В вашей корзине нет рецептов.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__recipes_shoppingcart_recipe_related__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
        )

        shopping_list = '\n'.join([
            f'{ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]}) - '
            f'{ingredient["total_amount"]}'
            for ingredient in ingredients
        ])
        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response


class TagViewSet(ReadOnlyModelViewSet):
    """ViewSet для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class IngredientViewSet(ReadOnlyModelViewSet):
    """ViewSet для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
