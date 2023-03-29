from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework.decorators import action
from .filters import IngredientFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import RecipeFilter
from .permissions import AuthorOrReadOnly, IsAdmin
from .serializers import (IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, TagSerializer)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdmin,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('^name',)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdmin,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):

    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user

        if user.is_anonymous:
            queryset = Recipe.objects.select_related(
                'author').prefetch_related('ingredients').annotate(
                    is_favorited=Exists(
                        Favorites.objects.filter(
                            user=None, recipe=OuterRef('pk'))),
                    is_in_shopping_cart=Exists(
                        ShoppingCart.objects.filter(
                            user=None, recipe=OuterRef('pk')))
            )
            return queryset

        favorites = Favorites.objects.filter(user=user, recipe=OuterRef('pk'))
        shopping_cart = ShoppingCart.objects.filter(
            user=user, recipe=OuterRef('pk')
        )

        queryset = Recipe.objects.select_related(
            'author').prefetch_related('ingredients').annotate(
            is_favorited=Exists(favorites),
            is_in_shopping_cart=Exists(shopping_cart)
        )
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        if not ShoppingCart.objects.filter(
                user=request.user
        ).exists():
            return Response(
                {'errors': 'В Корзине отсутствуют рецепты'},
                status=HTTP_400_BAD_REQUEST
            )
        ingredients = RecipeIngredient.objects.filter(
            recipe__baskets__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_list = ''
        for ingredient in ingredients:
            item = (f'* {ingredient["ingredient__name"]} '
                    f'({ingredient["ingredient__measurement_unit"]}) -- '
                    f'{ingredient["amount"]}\n\n'
                    )
            shopping_list += item
        return HttpResponse(shopping_list,
                            content_type='text/plain;charset=UTF-8'
                            )

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,)
            )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = ShortRecipeSerializer(recipe)
            if ShoppingCart.objects.get_or_create(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Этот рецепт уже есть в списке покупок'},
                    status=HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(
                user=request.user,
                recipe=recipe
            )
            return Response(serializer.data, status=HTTP_201_CREATED)

        ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,)
            )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = ShortRecipeSerializer(recipe)
            if Favorites.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Этот рецепт уже есть в Избранном'},
                    status=HTTP_400_BAD_REQUEST
                )
            Favorites.objects.create(
                user=request.user,
                recipe=recipe
            )
            return Response(serializer.data, status=HTTP_201_CREATED)

        Favorites.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=HTTP_204_NO_CONTENT)
