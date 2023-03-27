from base64 import b64decode

from django.core.files.base import ContentFile
from django.forms import BooleanField
from rest_framework.serializers import (BooleanField, CharField, ImageField,
                                        ModelSerializer, ValidationError)
from rest_framework.status import HTTP_400_BAD_REQUEST
from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.serializers import CustomUserSerializer


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ShortRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientRecipeSerializer(ModelSerializer):
    id = CharField(source='ingredient.id')
    name = CharField(source='ingredient.name')
    measurement_unit = CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='recipeingredient_set',
    )
    author = CustomUserSerializer(read_only=True)
    is_favorited = BooleanField(read_only=True)
    is_in_shopping_cart = BooleanField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def create(self, validated_data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipeTag.objects.create(tag_id=tag, recipe=recipe)

        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        tags = self.initial_data.get('tags')
        RecipeTag.objects.filter(recipe=instance).delete()
        RecipeTag.objects.bulk_create(
            RecipeTag(
                tag_id=tag,
                recipe=instance,

            ) for tag in tags)

        ingredients = self.initial_data.get('ingredients')
        RecipeIngredient.objects.filter(recipe=instance).delete()

        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients)

        instance.save()
        return instance

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        if not ingredients:
            raise ValidationError(
                {'ingredients': ('В рецепте должен быть использован '
                                 'минимум один ингредиент')
                 }
            )
        array_of_ingredients = []
        for ingredient in ingredients:

            if ingredient['id'] in array_of_ingredients:
                raise ValidationError(
                    detail='Ингредиенты не должны дублироваться',
                    code=HTTP_400_BAD_REQUEST
                )
            array_of_ingredients.append(ingredient['id'])
            if int(ingredient['amount']) < 1:
                raise ValidationError(
                    {'ingredients': ('Количество ингредиента в рецепте '
                                     'должно быть больше 0')
                     }
                )

        if not tags:
            raise ValidationError(
                {'tags': ('Рецепт должен быть привязан '
                          'минимум к одному тегу')
                 }
            )
        array_of_tags = set(tags)
        if len(array_of_tags) != len(tags):
            raise ValidationError(
                detail='Теги не должны дублироваться в рецепте',
                code=HTTP_400_BAD_REQUEST
            )
        return data
