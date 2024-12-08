from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Favourite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)

from .filters import IngredientFilter, RecipeQueryFilter
from .pagination import StandardPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (CompactRecipeSerializer, IngredientSerializer,
                          RecipeCreationSerializer, RecipeDetailSerializer,
                          TagSerializer)


class RecipeViewSet(ModelViewSet):
    """ViewSet для рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrReadOnly | IsAuthorOrReadOnly,)
    pagination_class = StandardPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeQueryFilter

    def perform_create(self, serializer):
        """Метод для сохранения рецепта с текущим пользователем как автором."""

        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Метод для выбора сериализатора в зависимости от действия."""

        if self.request.method in SAFE_METHODS:
            return RecipeDetailSerializer
        return RecipeCreationSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favourite(self, request, pk):
        """Метод для добавления/удаления рецепта в избранное."""

        if request.method == 'POST':
            return self.add_to(Favourite, request.user, pk)
        return self.delete_from(Favourite, request.user, pk)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        """Метод для добавления/удаления рецепта в корзину покупок."""

        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, pk)
        return self.delete_from(ShoppingCart, request.user, pk)

    def add_to(self, model, user, pk):
        """Метод для добавления рецепта в модель."""

        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = CompactRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        """Метод для удаления рецепта из модели."""

        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Метод для скачивания списка покупок."""

        user = request.user

        if not user.shopping_cart.exists():
            return Response(
                {'error': 'В вашей корзине нет рецептов.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=user
        )

        shopping_list = '\n'.join([
            f"{ingredient.ingredient.name} ({ingredient.ingredient.unit}) - "
            f"{ingredient.amount}"
            for ingredient in ingredients
        ])

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response


class TagViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для работы с тегами.
    Только чтение: список и детали.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для работы с ингредиентами.
    Только чтение: список и детали.
    Возможен поиск по названию.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
