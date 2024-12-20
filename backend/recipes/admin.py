from django.contrib import admin

from .models import Ingredient, Recipe, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для модели Recipe."""

    list_display = ('name', 'id', 'author', 'added_to_favorites_count',)
    readonly_fields = ('added_to_favorites_count',)
    list_filter = ('author', 'name', 'tags',)
    search_fields = ('name', 'author__username',)

    def added_to_favorites_count(self, obj):
        """Количество добавлений рецепта в избранное."""

        return obj.favorited_by.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для модели Ingredient."""

    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для модели Tag."""

    list_display = ('name', 'slug',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
