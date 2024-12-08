from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from .models import Follow, User


class UserAdmin(DefaultUserAdmin):
    """Кастомизация админ панели для управления пользователями."""

    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('email', 'username')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    """Кастомизация админ панели для управления подписками."""

    list_display = ('id', 'user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user__username', 'author__username')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
