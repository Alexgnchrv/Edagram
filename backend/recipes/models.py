from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Модель для ингредиентов."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название ингредиента'
    )
    unit = models.CharField(
        max_length=20,
        verbose_name='Единица измерения'
    )

    class Meta:
        """Мета-параметры модели."""

        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ['name']

    def __str__(self):
        """Метод строкового представления модели."""

        return f"{self.name} ({self.unit})"


class Tag(models.Model):
    """Модель для тегов рецептов."""

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название тега'
    )

    slug = models.SlugField(
        max_length=50,
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
        max_length=200,
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
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)'
    )

    class Meta:
        """Мета-параметры модели."""

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id',]

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
        validators=[
            MinValueValidator(1, 'Количество должно быть больше 0')
        ]
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


class Favourite(models.Model):
    'Модель для избранных рецептов.'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourited_by',
        verbose_name='Рецепт'
    )

    class Meta:
        """Мета-параметры модели."""

        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourite'
            )
        ]

    def __str__(self):
        """Метод строкового представления модели."""

        return f'{self.user} добавил {self.recipe} в избранное'


class ShoppingCart(models.Model):
    """Модель для корзины покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        """Мета-параметры модели."""

        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_cart'
            )
        ]

    def __str__(self):
        """Метод строкового представления модели."""

        return f'{self.user} добавил {self.recipe} в корзину'
