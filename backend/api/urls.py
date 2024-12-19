from django.urls import include, path

from rest_framework.routers import DefaultRouter

from users.views import StandartUserViewSet

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, short_url

app_name = 'api'

router = DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', StandartUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:pk>/short-url/', short_url, name='short-url'),
]
