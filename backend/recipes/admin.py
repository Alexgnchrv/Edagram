from django.contrib import admin

from .models import (Favourite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для модели Recipe."""

    list_display = ('name', 'id', 'author', 'added_to_favourites_count',)
    readonly_fields = ('added_to_favourites_count',)
    list_filter = ('author', 'name', 'tags',)
    search_fields = ('name', 'author__username',)

    def added_to_favourites_count(self, obj):
        """Количество добавлений рецепта в избранное."""

        return obj.favourited_by.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для модели Ingredient."""

    list_display = ('name', 'unit',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для модели Tag."""

    list_display = ('name', 'slug',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для модели ShoppingCart."""

    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    """Админка для модели Favourite."""

    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Админка для модели IngredientInRecipe."""

    list_display = ('recipe', 'ingredient', 'amount',)
    search_fields = ('recipe__name', 'ingredient__name',)
