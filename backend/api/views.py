from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Favourite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)

from .filters import IngredientFilter
from .pagination import StandardPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (CompactRecipeSerializer, IngredientSerializer,
                          RecipeCreationSerializer, RecipeDetailSerializer,
                          TagSerializer)


@require_GET
def short_url(request, pk=None):
    try:
        get_object_or_404(Recipe, pk=pk)
        return redirect(f'/recipes/{pk}/')
    except Http404:
        raise ValidationError(f'Рецепт "{pk}" не существует.')


class RecipeViewSet(ModelViewSet):
    """ViewSet для рецептов."""

    queryset = Recipe.objects.all()
    pagination_class = StandardPagination
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_url = reverse('api:short-url', kwargs={'pk': recipe.pk})
        return Response({
            'short-link': request.build_absolute_uri(short_url)
        }, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """Метод для сохранения рецепта с текущим пользователем как автором."""

        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Метод для выбора сериализатора в зависимости от действия."""

        if self.request.method in SAFE_METHODS:
            return RecipeDetailSerializer
        return RecipeCreationSerializer

    def get_queryset(self):
        """Переопределение получения QuerySet для фильтрации."""

        user = self.request.user
        is_favorited = self.request.query_params.get(
            'is_favorited'
        )
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        tags = self.request.query_params.getlist('tags')
        author = self.request.query_params.get('author')

        queryset = super().get_queryset()
        if author:
            queryset = queryset.filter(author__id=author)
        if is_favorited == '1' and user.is_authenticated:
            queryset = queryset.filter(favorited_by__user=user)
        if is_in_shopping_cart == '1' and user.is_authenticated:
            queryset = queryset.filter(is_in_shopping_cart__user=user)
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        return queryset

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        """Метод для добавления/удаления рецепта в избранное."""

        if request.method == 'POST':
            if Favourite.objects.filter(user=request.user,
                                        recipe__id=pk).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен в избранное!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe = get_object_or_404(Recipe, id=pk)
            Favourite.objects.create(user=request.user, recipe=recipe)
            serializer = CompactRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            obj = Favourite.objects.filter(user=request.user, recipe=recipe)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт не найден в избранном!'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({'errors': 'Метод не поддерживается.'},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        """Метод для добавления/удаления рецепта в корзину покупок."""

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=request.user,
                                           recipe__id=pk).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен в корзину!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe = get_object_or_404(Recipe, id=pk)
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = CompactRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            obj = ShoppingCart.objects.filter(user=request.user, recipe=recipe)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт не найден в корзине!'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({'errors': 'Метод не поддерживается.'},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Метод для скачивания списка покупок."""

        user = request.user

        if not user.shopping_cart.exists():
            return Response(
                {'error': 'В вашей корзине нет рецептов.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__is_in_shopping_cart__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
        )

        shopping_list = '\n'.join([
            f"{ingredient['ingredient__name']} "
            f"({ingredient['ingredient__measurement_unit']}) - "
            f"{ingredient['total_amount']}"
            for ingredient in ingredients
        ])

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response


class TagViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для работы с тегами.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для работы с ингредиентами.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
