from re import match

from django.forms import ValidationError
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.status import HTTP_400_BAD_REQUEST
from users.models import User

from .models import Subscriptions


class RegistreUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'username', 'password')
        write_only_field = ('password',)

    def validate_username(self, value):
        if not match(r'[\w.@+\-]+', value):
            raise ValidationError('Некорректный логин')
        return value


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name',
            'last_name', 'username', 'is_subscribed'
        )
        write_only_field = ('password',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscriptions.objects.filter(
            user=request.user,
            author=obj.id
        ).exists()


class FollowSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        from api.serializers import ShortRecipeSerializer
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = ShortRecipeSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data

    def validate(self, data):
        user = self.context.get('request').user
        author = self.instance
        if user == author:
            raise ValidationError(
                detail='Пользователь не может подписаться сам на себя',
                code=HTTP_400_BAD_REQUEST
            )
        if Subscriptions.objects.filter(
            user=user,
            author=author
        ).exists():
            raise ValidationError(
                detail=('Пользователь не может подписаться '
                        'на другого пользователя дважды'),
                code=HTTP_400_BAD_REQUEST
            )
        return data
