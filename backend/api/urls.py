from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import StandartUserViewSet

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                    short_url_redirect)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('users', StandartUserViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('<str:short_code>/', short_url_redirect, name='short-url-redirect'),
]
