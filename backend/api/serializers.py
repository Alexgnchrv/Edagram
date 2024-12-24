from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (CharField, IntegerField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        Serializer, ValidationError)

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
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
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'avatar',)

    def get_is_subscribed(self, obj):
        """
        Проверяет, подписан ли текущий пользователь на данного автора.
        """

        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return obj.following.filter(user=request.user).exists()
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


class AvatarUpdateSerializer(ModelSerializer):
    """
    Сериализатор для обновления аватара пользователя.
    """

    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = ('avatar',)


class FollowSerializer(ModelSerializer):
    """
    Сериализатор для подписок пользователя.
    """

    email = ReadOnlyField(source='author.email')
    id = ReadOnlyField(source='author.id')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    avatar = Base64ImageField(source='author.avatar', required=False)
    recipes = SerializerMethodField()
    is_subscribed = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'recipes_count', 'recipes', 'is_subscribed', 'avatar',
        )
        read_only_fields = ('email', 'username', 'is_subscribed')

    def get_recipes_count(self, obj):
        """
        Получение количества рецептов автора.
        """

        return obj.author.recipes.count()

    def get_recipes(self, obj):
        """
        Получение списка рецептов с ограничением по количеству.
        """

        recipes = obj.author.recipes.all()
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes_limit = int(recipes_limit)
            recipes = recipes[:recipes_limit]
        return CompactRecipeSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        """
        Проверяет, подписан ли текущий пользователь на данного автора.
        """

        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return obj.user == request.user


class TagSerializer(ModelSerializer):
    """
    Сериализатор для тегов.
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientInRecipeSerializer(ModelSerializer):
    """
    Сериализатор для отображения ингредиентов в рецепте.
    """

    id = IntegerField(source='ingredient.id')
    name = CharField(source='ingredient.name')
    measurement_unit = CharField(
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
        fields = (
            'id', 'name', 'text', 'ingredients', 'author',
            'is_favorited', 'is_in_shopping_cart', 'cooking_time',
            'tags', 'image',
        )

    def get_is_favorited(self, obj):
        """
        Проверяет, добавлен ли рецепт в избранное текущим пользователем.
        """

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.recipes_favourite_recipe_related.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Проверяет, находится ли рецепт в корзине покупок текущего пользователя.
        """

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return (obj.recipes_shoppingcart_recipe_related
                .filter(user=user).exists())


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
        fields = ('id', 'name', 'image', 'cooking_time',)


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

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount',)

    def validate_amount(self, value):
        """Проверка на корректность количества ингредиента."""
        if value <= 0:
            raise ValidationError(
                'Количество ингредиента должно быть больше 0!')
        return value

    def validate_id(self, value):
        """
        Проверяет, существует ли ингредиент с указанным id.
        """
        if not Ingredient.objects.filter(id=value).exists():
            raise ValidationError(
                f'Ингредиента с id {value} не существует!'
            )
        return value

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

    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
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
        Проверяет, что ингредиенты не пусты и уникальны.
        """
        if not value:
            raise ValidationError(
                'Необходимо указать хотя бы один ингредиент!')

        seen = set()
        for ingredient in value:
            ingredient_id = ingredient['id']
            if ingredient_id in seen:
                raise ValidationError('Ингредиенты должны быть уникальными!')
            seen.add(ingredient_id)

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
                {'tags': 'This field is required.'}
            )
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredient_links', None)
        if ingredients is None:
            raise ValidationError(
                {'ingredient_links': 'This field is required.'}
            )
        instance.ingredients.clear()
        self._add_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def _add_ingredients(self, recipe, ingredients):
        """
        Создаёт связи между рецептом и ингредиентами.
        """

        ingredient_objects = Ingredient.objects.filter(
            id__in=[ingredient['id'] for ingredient in ingredients])
        ingredients_sorted = sorted(ingredient_objects,
                                    key=lambda x: x.name.lower())

        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient,
                amount=next(
                    item['amount'] for item in ingredients
                    if item['id'] == ingredient.id)
            ) for ingredient in ingredients_sorted
        ])


class AddToModelSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = None
        fields = ('user', 'recipe')

    def __init__(self, *args, **kwargs):
        model = kwargs.pop('model', None)
        super().__init__(*args, **kwargs)
        if model:
            self.Meta.model = model

    def validate(self, data):
        """Проверка существования записи перед добавлением."""
        model = self.Meta.model
        if model.objects.filter(user=data['user'],
                                recipe=data['recipe']).exists():
            raise ValidationError('Рецепт уже добавлен!')
        return data

    @transaction.atomic
    def create(self, validated_data):
        """Создание записи в модели (добавление рецепта)."""
        model = self.Meta.model
        return model.objects.create(**validated_data)


class CreateFollowSerializer(Serializer):
    """Сериализатор для создания подписки."""

    user = PrimaryKeyRelatedField(queryset=User.objects.all(),
                                  required=False)
    author = PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate(self, data):
        user = self.context.get('request').user
        author = data.get('author')

        if user == author:
            raise ValidationError(
                'Вы не можете подписаться на самого себя.')

        if Follow.objects.filter(user=user, author=author).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя.')

        return data

    def create(self, validated_data):
        """Создаем объект подписки."""

        user = self.context.get('request').user
        author = validated_data.get('author')

        follow = Follow.objects.create(user=user, author=author)
        return follow
