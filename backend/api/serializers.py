import base64
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import Follow
from recipes.models import (
    Tag,
    Product,
    Recipe,
    PurchaseList,
    Favorite,
    IngredientToRecipe
)

WRONG_PASSWORD = 'Введен неверный пароль'
SAME_PASSWORD = 'Старый и новый пароли не могут совпадать!'

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с пользователями."""

    is_subscribed = serializers.SerializerMethodField()
    password = serializers.CharField(max_length=150, write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        """Метод проверяет подписку на пользователя."""
        if self.context['request'].user.is_authenticated:
            current_user = self.context['request'].user
            return Follow.objects.filter(
                author__username=obj.username,
                follower=current_user
            ).exists()
        return False

    def create(self, validated_data):
        """Метод создания пользователя."""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password is not None:
            user.set_password(password)
            user.save()
        return user


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""

    current_password = serializers.CharField(max_length=150, write_only=True)
    new_password = serializers.CharField(max_length=150, write_only=True)

    def validate_current_password(self, current_password):
        """Метод валидации текущего пароля."""

        user = self.context['request'].user
        if not user.check_password(current_password):
            raise serializers.ValidationError(WRONG_PASSWORD)
        return current_password

    def validate_new_password(self, new_password):
        """Метод проверки совпадения текущего и нового пароля."""

        current_password = self.initial_data.get('current_password')
        if current_password == new_password:
            raise serializers.ValidationError(SAME_PASSWORD)
        return new_password


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок с выводом рецептов."""

    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'username',
            'first_name',
            'last_name',
            'id',
            'email',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        recipes = obj.author.recipes.all()
        serialized_recipes = []
        for recipe in recipes:
            serialized_recipe = {
                'id': recipe.id,
                'name': recipe.name,
                'image': getattr(recipe.image, 'url'),
                'cooking_time': recipe.cooking_time
            }
            serialized_recipes.append(serialized_recipe)
        return serialized_recipes

    def get_recipes_count(self, obj):
        return obj.author.recipes.all().count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов."""

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientToPostRecipeSerializer(serializers.Serializer):
    """Сериализатор ингридиентов."""

    id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    amount = serializers.IntegerField()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов для рецепта."""

    id = serializers.IntegerField(source='product.id')
    name = serializers.CharField(source='product.name', required=False)
    measurement_unit = serializers.CharField(
        source='product.measurement_unit',
        required=False
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientToRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    id = serializers.IntegerField(source='recipe.id')
    name = serializers.CharField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image')
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class PurchaseListSerializer(serializers.ModelSerializer):
    """Сериализатор для добавленя и удаления рецепта в/из списка покупок."""

    id = serializers.IntegerField(source='recipe.id')
    name = serializers.CharField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image')
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')

    class Meta:
        model = PurchaseList
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class ReturnPurchaseListSerializer(serializers.ModelSerializer):
    """Сериализатор для возврата списка ингридиентов."""

    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseList
        fields = ('ingredients')

    def get_ingredients(self, obj):
        pass


class Base64ToImage(serializers.ImageField):
    """Сериализатор для преобразования формата изображения."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор возвращаемых рецептов."""
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='ingredientsincide'
    )
    author = UserSerializer(default=serializers.CurrentUserDefault())
    image = Base64ToImage()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'cooking_time',
            'text',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_favorited.filter(author=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_in_shopping_cart.filter(author=request.user).exists()
        return False


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, read_only=False
    )
    ingredients = IngredientToPostRecipeSerializer(many=True)
    image = Base64ToImage()
    author = UserSerializer(default=serializers.CurrentUserDefault())
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'name',
            'image',
            'text',
            'cooking_time',
            'ingredients',
            'author'
        )

    def create(self, validated_data):
        base_recipe = Recipe.objects.create(
            author=validated_data['author'],
            image=validated_data['image'],
            name=validated_data['name'],
            text=validated_data['text'],
            cooking_time=validated_data['cooking_time']
        )
        base_recipe.tags.set(validated_data['tags'])
        base_recipe.save()
        ingredients_to_create = []
        for ingredient in validated_data['ingredients']:
            ingredients_to_create.append(
                IngredientToRecipe(
                    recipe=base_recipe,
                    product=ingredient['id'],
                    amount=ingredient['amount']
                )
            )
        IngredientToRecipe.objects.bulk_create(ingredients_to_create)
        return base_recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.tags.set(validated_data.get('tags', instance.tags.all()))
        ingredients_data = validated_data.get('ingredients')
        if ingredients_data is not None:
            instance.ingredients.clear()
            ingredients_to_create = [
                IngredientToRecipe(
                    recipe=instance,
                    product=ingredient_data.get('id'),
                    amount=ingredient_data.get('amount')
                )
                for ingredient_data in ingredients_data
                if ingredient_data.get('id') and ingredient_data.get('amount')
            ]
            IngredientToRecipe.objects.bulk_create(ingredients_to_create)
        instance.save()
        return instance
