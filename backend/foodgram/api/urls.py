from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = routers.SimpleRouter()

router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
