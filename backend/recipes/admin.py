from django.contrib import admin

from .models import (Favourite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    fields = ('ingredient', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для модели Recipe."""

    list_display = ('name', 'id', 'author', 'added_to_favorites_count',
                    'tags_display', 'ingredients_display',)
    readonly_fields = ('added_to_favorites_count',)
    list_filter = ('author', 'name', 'tags',)
    search_fields = ('name', 'author__username',)
    ordering = ('-id',)
    actions = ['delete_selected']
    list_per_page = 25
    inlines = [IngredientInRecipeInline]

    @admin.display(description='Количество добавлений в избранное')
    def added_to_favorites_count(self, obj):
        """Количество добавлений рецепта в избранное."""

        return obj.recipes_favourite_recipe_related.count()

    @admin.display(description='Теги')
    def tags_display(self, obj):
        """Отображение тегов в списке рецептов."""

        return ', '.join([tag.name for tag in obj.tags.all()])

    @admin.display(description='Ингредиенты')
    def ingredients_display(self, obj):
        """Отображение ингредиентов в списке рецептов."""

        return ', '.join(
            [f'{ingredient_in_recipe.ingredient.name} '
             f'({ingredient_in_recipe.amount})'
             for ingredient_in_recipe in
             IngredientInRecipe.objects.filter(recipe=obj)]
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для модели Ingredient."""

    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('-id',)
    actions = ['delete_selected']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для модели Tag."""

    list_display = ('name', 'slug',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-id',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для модели ShoppingCart."""

    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)
    ordering = ('-id',)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Админка для модели IngredientInRecipe."""

    list_display = ('recipe', 'ingredient', 'amount',)
    search_fields = ('recipe__name', 'ingredient__name',)
    ordering = ('-id',)


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    """Админка для модели Favourite."""
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')
    ordering = ('-id',)
