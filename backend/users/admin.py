from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import Follow, User


class UserAdmin(DefaultUserAdmin):
    """Кастомизация админ панели для управления пользователями."""

    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name', 'followers_count', 'recipes_count')
    list_filter = ('email', 'username')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'

    @admin.display(description='Количество подписчиков')
    def followers_count(self, obj):
        return obj.follower.count()
    followers_count.admin_order_field = 'follower'
    followers_count.short_description = 'Количество подписчиков'

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()
    recipes_count.admin_order_field = 'recipes'
    recipes_count.short_description = 'Количество рецептов'


class FollowAdmin(admin.ModelAdmin):
    """Кастомизация админ панели для управления подписками."""

    list_display = ('id', 'user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user__username', 'author__username')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
