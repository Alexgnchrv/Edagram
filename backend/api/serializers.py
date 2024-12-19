from django.db import transaction
from django.shortcuts import get_object_or_404

from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        Serializer, ValidationError)

from recipes.models import (Favourite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow, User


class StandartUserSerializer(UserSerializer):
    """
    Сериализатор для отображения информации о пользователе.
    """

    is_subscribed = SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta:
        """Мета-параметры сериализатора."""

        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'avatar']

    def get_is_subscribed(self, obj):
        """Проверяет подписку."""

        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return (Follow.objects.
                    filter(user=request.user, author=obj).exists())
        return False


class UserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор для создания нового пользователя.
    """

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
            'id',
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }


class AvatarUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления аватара пользователя.
    """

    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = ['avatar']


class FollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подписок пользователя.
    """

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'recipes_count', 'recipes', 'is_subscribed', 'avatar'
        )
        read_only_fields = ('email', 'username', 'is_subscribed')

    def validate(self, data):
        """
        Валидация для проверки.
        """

        user = self.context.get('request').user
        author = self.instance

        if Follow.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        """
        Получение количества рецептов автора.
        """

        return obj.recipes.count()

    def get_recipes(self, obj):
        """
        Получение списка рецептов с ограничением по количеству.
        """

        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')

        recipes = obj.recipes.all()
        if recipes_limit:
            recipes_limit = int(recipes_limit)
            recipes = recipes[:recipes_limit]
            serializer = CompactRecipeSerializer(recipes, many=True,
                                                 read_only=True)
            return serializer.data

        return CompactRecipeSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        """
        Проверяет, подписан ли текущий пользователь на данного автора.
        """

        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return obj.follower.filter(user=request.user).exists()
        return False


class TagSerializer(ModelSerializer):
    """
    Сериализатор для тегов.
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения ингредиентов в рецепте.
    """

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')


class RecipeDetailSerializer(ModelSerializer):
    """
    Сериализатор для получения детальной информации о рецепте.
    """

    author = StandartUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredient_links'
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()

    class Meta:
        """
        Мета-параметры сериализатора.
        """

        model = Recipe
        fields = [
            'id', 'name', 'text', 'ingredients', 'author',
            'is_favorited', 'is_in_shopping_cart', 'cooking_time',
            'tags', 'image',
        ]

    def get_is_favorited(self, obj):
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
    """
    Сериализатор для отображения сокращенной информации о рецепте.
    """

    image = Base64ImageField()

    class Meta:
        """
        Мета-параметры сериализатора.
        """

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializer(ModelSerializer):
    """
    Сериализатор для ингредиентов.
    """

    class Meta:
        """
        Мета-параметры сериализатора.
        """

        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientInputSerializer(Serializer):
    """
    Сериализатор для ввода ингредиентов в рецепт.
    """

    id = IntegerField()
    amount = IntegerField()
    name = SerializerMethodField()
    measurement_unit = SerializerMethodField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount', 'name', 'measurement_unit')

    def get_name(self, ingredient_in_recipe):
        """
        Получает имя ингредиента.
        """

        return ingredient_in_recipe.ingredient.name

    def get_measurement_unit(self, ingredient_in_recipe):
        """
        Получает единицу измерения ингредиента.
        """

        return ingredient_in_recipe.ingredient.measurement_unit


class RecipeCreationSerializer(ModelSerializer):
    """
    Сериализатор для создания и обновления рецептов.
    """

    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = RecipeIngredientInputSerializer(
        many=True,
        source='ingredient_links'
    )
    image = Base64ImageField()

    class Meta:
        """
        Мета-параметры сериализатора.
        """

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

    def to_representation(self, instance):
        """Метод представления модели"""

        serializer = RecipeDetailSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data

    def validate_ingredients(self, value):
        """
        Проверяет, что ингредиенты не пусты и корректны.
        """

        if not value:
            raise ValidationError(
                'Необходимо указать хотя бы один ингредиент!'
            )
        seen = set()
        for ingredient in value:
            ingredient_id = ingredient['id']
            if ingredient_id in seen:
                raise ValidationError('Ингредиенты должны быть уникальными!')
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f'Ингредиента с id {ingredient_id} не существует!'
                )
            if int(ingredient['amount']) <= 0:
                raise ValidationError(
                    'Количество ингредиентов должно быть больше 0!'
                )
            seen.add(ingredient['id'])
        return value

    def validate_tags(self, value):
        """
        Проверяет, что теги не пусты и уникальны.
        """

        if not value:
            raise ValidationError('Необходимо указать хотя бы один тег!')
        if len(set(value)) != len(value):
            raise ValidationError('Теги должны быть уникальными!')
        return value

    def validate_image(self, value):
        if not value:
            raise ValidationError('Поле "image" не может быть пустым.')
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Время приготовления должно быть не менее одной минуты."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        """
        Создаёт рецепт с тегами и ингредиентами.
        """

        ingredients = validated_data.pop('ingredient_links')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._add_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Обновляет рецепт.
        """

        tags = validated_data.pop('tags', None)
        if tags is None:
            raise ValidationError(
                {"tags": "This field is required."}
            )
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredient_links', None)
        if ingredients is None:
            raise ValidationError(
                {"ingredient_links": "This field is required."}
            )
        instance.ingredients.clear()
        self._add_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def _add_ingredients(self, recipe, ingredients):
        """
        Создаёт связи между рецептом и ингредиентами.
        """

        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])
