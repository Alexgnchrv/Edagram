import random
import string

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (INGREDIENT_NAME_MAX_LENGTH, MAX_COOKING_TIME,
                        MEASUREMENT_UNIT_MAX_LENGTH, MIN_COOKING_TIME,
                        RECIPE_NAME_MAX_LENGTH, SHORTURL_SHORTCODE_MAX_LENGTH,
                        TAG_NAME_MAX_LENGTH, TAG_SLUG_MAX_LENGTH)

User = get_user_model()


class Ingredient(models.Model):
    """Модель для ингредиентов."""

    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        """Мета-параметры модели."""

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        """Метод строкового представления модели."""

        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    """Модель для тегов рецептов."""

    name = models.CharField(
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Название тега'
    )

    slug = models.SlugField(
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True,
        blank=True,
        verbose_name='Уникальный слаг'
    )

    class Meta:
        """Мета-параметры модели."""

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        """Метод строкового представления модели."""

        return self.name


class Recipe(models.Model):
    """Модель для рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации'
    )
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name=('Время приготовления (в минутах)'),
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                ('Время приготовления должно быть не менее одной минуты')),
            MaxValueValidator(
                MAX_COOKING_TIME,
                ('Время приготовления не может превышать 10 000 минут'))
        ]
    )

    class Meta:
        """Мета-параметры модели."""

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id', ]

    def __str__(self):
        """Метод строкового представления модели."""

        return self.name


class IngredientInRecipe(models.Model):
    """Модель для связи рецепта с ингредиентами."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_links',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_links',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
    )

    class Meta:
        """Мета-параметры модели."""

        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        """Метод строкового представления модели."""

        return f'{self.ingredient} для {self.recipe}'


class BaseUserRecipeRelation(models.Model):
    """Базовая модель для связи User и Recipe."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_user_related",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_recipe_related",
        verbose_name="Рецепт"
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="%(app_label)s_%(class)s_user_recipe_unique"
            )
        ]

    def __str__(self):
        return f"{self.user} добавил {self.recipe}"


class Favourite(BaseUserRecipeRelation):
    """Модель для избранных рецептов."""

    class Meta(BaseUserRecipeRelation.Meta):
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"

    def __str__(self):
        return f"{self.user} добавил {self.recipe} в избранное"


class ShoppingCart(BaseUserRecipeRelation):
    """Модель для корзины покупок."""

    class Meta(BaseUserRecipeRelation.Meta):
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"

    def __str__(self):
        return f"{self.user} добавил {self.recipe} в корзину"


class ShortURL(models.Model):
    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        related_name="short_url")
    short_code = models.CharField(
        max_length=SHORTURL_SHORTCODE_MAX_LENGTH,
        unique=True)
    created_at = models.DateTimeField(
        auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self.generate_short_code()
        super().save(*args, **kwargs)

    def generate_short_code(self):
        """Генерация случайного короткого кода."""
        return ''.join(
            random.choices(string.ascii_letters + string.digits, k=8))

    def __str__(self):
        return self.short_code
