from django.db import transaction
from django.shortcuts import get_object_or_404

from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField, Serializer,
                                        ValidationError)

from recipes.models import (Favourite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow, User


class StandartUserSerializer(UserSerializer):
    """Сериализатор для отображения информации о пользователе."""

    is_subscribed = SerializerMethodField()

    class Meta:
        """Мета-параметры сериализатора."""

        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed']

    def get_is_subscribed(self, obj):
        """Проверяет подписку."""

        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return obj.following.filter(user=request.user).exists()
        return False


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
        )


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок пользователя (Follow)."""

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'recipes_count', 'recipes', 'is_subscribed'
        )
        read_only_fields = ('email', 'username', 'is_subscribed')

    def validate(self, data):
        """Валидация для проверки."""

        user = self.context.get('request').user
        author = self.instance

        if Follow.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code='subscription_error'
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code='self_subscription_error'
            )
        return data

    def get_recipes_count(self, obj):
        """Получение количества рецептов автора."""

        return obj.recipes.count()

    def get_recipes(self, obj):
        """Получение списка рецептов с ограничением по количеству."""

        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')

        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                recipes = recipes[:recipes_limit]
            except ValueError:
                raise ValidationError(
                    'Неверное значение для параметра recipes_limit.'
                )

        return CompactRecipeSerializer(recipes, many=True).data


class RecipeIngredientSerializer(ModelSerializer):
    class Meta:
        """Мета-параметры сериализатора."""

        model = Ingredient
        fields = ['id', 'name', 'unit']


class RecipeDetailSerializer(ModelSerializer):
    """Сериализатор для получения детальной информации о рецепте."""

    author = StandartUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    is_favourited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        """Мета-параметры сериализатора."""

        model = Recipe
        fields = [
            'id', 'name', 'text', 'ingredients', 'author',
            'is_favourited', 'is_in_shopping_cart', 'cooking_time'
        ]

    def get_is_favourited(self, obj):
        """
        Проверяет, добавлен ли рецепт в избранное текущим пользователем.
        """

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favourite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Проверяет, находится ли рецепт в корзине покупок текущего пользователя.
        """

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class CompactRecipeSerializer(ModelSerializer):
    """Сериализатор для отображения сокращенной информации о рецепте."""

    image = Base64ImageField()

    class Meta:
        """Мета-параметры сериализатора."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializer(ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        """Мета-параметры сериализатора."""

        model = Ingredient
        fields = (
            'id',
            'name',
            'unit',
        )


class RecipeIngredientInputSerializer(Serializer):
    """Сериализатор для ввода ингредиентов в рецепт."""

    id = IntegerField()
    amount = IntegerField()
    name = SerializerMethodField()
    unit = SerializerMethodField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount', 'name', 'unit')

    def get_name(self, ingredient_in_recipe):
        """Получает имя ингредиента."""

        return ingredient_in_recipe.ingredient.name

    def get_unit(self, ingredient_in_recipe):
        """Получает единицу измерения ингредиента."""

        return ingredient_in_recipe.ingredient.unit


class RecipeCreationSerializer(ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientInputSerializer(
        many=True,
    )
    image = Base64ImageField()

    class Meta:
        """Мета-параметры сериализатора"""

        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        """Проверяет, что ингредиенты не пусты и корректны."""

        if not value:
            raise ValidationError(
                'Необходимо указать хотя бы один ингредиент!'
            )
        seen = set()
        for ingredient in value:
            if ingredient['id'] in seen:
                raise ValidationError('Ингредиенты должны быть уникальными!')
            if int(ingredient['amount']) <= 0:
                raise ValidationError(
                    'Количество ингредиентов должно быть больше 0!'
                )
            seen.add(ingredient['id'])
        return value

    def validate_tags(self, value):
        """Проверяет, что теги не пусты и уникальны."""

        if not value:
            raise ValidationError('Необходимо указать хотя бы один тег!')
        if len(set(value)) != len(value):
            raise ValidationError('Теги должны быть уникальными!')
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Создаёт рецепт с тегами и ингредиентами."""

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._add_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет рецепт."""

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.ingredients.clear()
        self._add_ingredients(instance, ingredients)
        return instance

    def _add_ingredients(self, recipe, ingredients):
        """Создаёт связи между рецептом и ингредиентами."""

        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])


class TagSerializer(ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
