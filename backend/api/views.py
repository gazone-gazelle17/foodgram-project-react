from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from recipes.models import (
    Tag,
    Product,
    Favorite,
    Recipe,
    PurchaseList,
    IngredientToRecipe
)
from users.models import Follow
from .serializers import (
    FavoriteSerializer, FollowSerializer,
    IngredientSerializer, PurchaseListSerializer,
    RecipeSerializer, ReturnPurchaseListSerializer,
    SetPasswordSerializer, TagSerializer, UserSerializer,
    CreateRecipeSerializer
)
from .utils import JsonToPdf
from .permissions import OwnerOrReadOnly


User = get_user_model()


class UserListCreateView(generics.ListCreateAPIView):
    """Обрабатывает запрос списка и создание нового пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """Переопределяет метод post."""
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            del data['is_subscribed']
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class UserDetailView(generics.RetrieveAPIView):
    """
    Возвращает ответ на запрос конкретного пользователя.
    Работает так же с текущим пользователем ('me').
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        if self.kwargs.get('pk', None) == 'me':
            self.kwargs['pk'] = self.request.user.pk
        return super(UserDetailView, self).get_object()


class SetPasswordView(generics.UpdateAPIView):
    """Изменяет пароль."""

    serializer_class = SetPasswordSerializer

    def get_object(self):
        """Получает текущего пользователя."""
        return self.request.user

    def post(self, request, *args, **kwargs):
        """Меняет базовый метод post на update."""
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Переопределяет метод update."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {"message": "Пароль успешно изменен"},
            status=status.HTTP_200_OK
        )

    def perform_update(self, serializer):
        """Добавляет проверку пароля в метод update."""
        user = self.get_object()
        user.set_password(serializer.validated_data['new_password'])
        user.save()


class TagsViewSet(viewsets.ModelViewSet):
    """Возвращает список и отдельный тег."""

    serializer_class = TagSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Tag.objects.all()
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = tags.split(',')
            queryset = Tag.objects.filter(name__in=tag_list)
        return queryset


class IngredientViewset(viewsets.ModelViewSet):
    """Возвращает список и отдельный ингредиент."""

    queryset = Product.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['name']
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering = ('-pub_date',)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return CreateRecipeSerializer
        return RecipeSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if request.query_params.get('is_favorited'):
            recipes_pk = Favorite.objects.filter(
                author=request.user).values_list('recipe_id', flat=True)
            queryset = queryset.filter(id__in=recipes_pk)
        if request.query_params.get('is_in_shopping_cart'):
            recipes_pk = PurchaseList.objects.filter(
                author=request.user).values_list('recipe_id', flat=True)
            queryset = queryset.filter(id__in=recipes_pk)
        if request.query_params.get('tags'):
            tags = Tag.objects.filter(
                slug__in=request.query_params.getlist('tags'))
            queryset = queryset.filter(
                tags__in=tags).distinct()
        if request.query_params.get('author'):
            queryset = queryset.filter(
                author_id=request.query_params['author'])
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if Recipe.objects.filter(
            author=request.user,
            name=request.data['name']
        ).exists():
            return Response(
                {"error": "Такой рецепт уже существует."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(RecipeSerializer(
            result, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def partial_update(self, request, *args, **kwargs):
        recipe_id = self.kwargs['pk']
        recipe_to_update = Recipe.objects.get(pk=recipe_id)
        serializer = self.get_serializer(
            instance=recipe_to_update, data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(RecipeSerializer(
            result, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Вы успешно удалили рецепт."},
            status=status.HTTP_204_NO_CONTENT
        )


class FollowListView(generics.ListAPIView,):
    """Обрабатывает запрос списка подписок."""

    serializer_class = FollowSerializer
    permission_classes = [OwnerOrReadOnly]

    def get_queryset(self):
        current_user = self.request.user
        return Follow.objects.filter(follower=current_user)


class FollowRetrieveDeleteView(
    generics.CreateAPIView,
    generics.DestroyAPIView
):
    """Обрабатывает запрос создания и удаления подписки."""

    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def post(self, request, *args, **kwargs):
        """Создает подписку."""
        author_id = self.kwargs['pk']
        try:
            author = User.objects.get(pk=author_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        if Follow.objects.filter(
            author=author,
            follower=self.request.user
        ).exists():
            return Response(
                {"error": "Пользователь уже подписан"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if author == self.request.user:
            return Response(
                {"error": "Вы не можете подписаться на себя."},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow_instance = Follow.objects.create(
            author=author,
            follower=self.request.user
        )
        serializer = FollowSerializer(
            follow_instance,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """Удаляет подписку."""
        author_id = self.kwargs['pk']
        author = User.objects.get(pk=author_id)
        if Follow.objects.filter(
            author=author,
            follower=self.request.user
        ).exists():
            Follow.objects.filter(
                author=author,
                follower=self.request.user
            ).delete()
            return Response(
                {"message": "Вы успешно отписались от пользователя."},
                status=status.HTTP_204_NO_CONTENT
            )


class FavoriteRetrieveDeleteView(
    generics.CreateAPIView,
    generics.DestroyAPIView
):
    """Добавляет и удаляет рецепты из избранного."""

    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('recipe__tags',)

    def post(self, request, *args, **kwargs):
        """Добавляет рецепт."""
        recipe_id = self.kwargs['pk']
        favorite_recipe = Recipe.objects.get(pk=recipe_id)
        if Favorite.objects.filter(
                author=request.user,
                recipe=favorite_recipe
        ).exists():
            return Response(
                {"message": "Такая запись уже есть."},
                status=status.HTTP_400_BAD_REQUEST
            )
        new_favorite = Favorite.objects.create(
            author=request.user,
            recipe=favorite_recipe
        )
        serializer = FavoriteSerializer(new_favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """Удаляет рецепт."""
        recipe_id = self.kwargs['pk']
        recipe_to_delete = Recipe.objects.get(pk=recipe_id)
        if Favorite.objects.filter(
                author=request.user,
                recipe=recipe_to_delete
        ).exists():
            Favorite.objects.get(
                author=request.user,
                recipe=recipe_to_delete
            ).delete()
            return Response(
                {"message": "Запись успешно удалена."},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {"message": "Такой записи не существует."},
            status=status.HTTP_400_BAD_REQUEST
        )


class ShoppingListRetrieveDeleteView(
    generics.CreateAPIView,
    generics.DestroyAPIView
):
    """Добавляет и удаляет рецепты из списка покупок."""

    queryset = PurchaseList.objects.all()
    serializer_class = PurchaseListSerializer

    def post(self, request, *args, **kwargs):
        """Добавляет рецепт."""
        recipe_id = self.kwargs['pk']
        favorite_recipe = Recipe.objects.get(pk=recipe_id)
        if PurchaseList.objects.filter(
                author=request.user,
                recipe=favorite_recipe
        ).exists():
            return Response(
                {"message": "Такая запись уже есть."},
                status=status.HTTP_400_BAD_REQUEST
            )
        new_favorite = PurchaseList.objects.create(
            author=request.user,
            recipe=favorite_recipe
        )
        serializer = PurchaseListSerializer(new_favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """Удаляет рецепт."""
        recipe_to_delete = self.kwargs['pk']
        if PurchaseList.objects.filter(
                author=request.user,
                recipe=recipe_to_delete
        ).exists():
            PurchaseList.objects.get(
                author=request.user,
                recipe=recipe_to_delete
            ).delete()
            return Response(
                {"message": "Запись успешно удалена."},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {"message": "Такой записи не существует."},
            status=status.HTTP_400_BAD_REQUEST
        )


class GetShoppingListView(generics.RetrieveAPIView):
    """Возвращает список покупок."""

    queryset = PurchaseList.objects.all()
    serializer_class = ReturnPurchaseListSerializer
    permission_classes = [OwnerOrReadOnly]

    def get(self, request):
        purchases = PurchaseList.objects.filter(author=self.request.user)
        final_ingredients = {}
        for purchase in purchases:
            recipe = purchase.recipe
            recipe_name = recipe.name
            ingredients_to_recipe = IngredientToRecipe.objects.filter(
                recipe=recipe
            )
            ingredients = []
            ingredient_data = {}
            for ingredient_to_recipe in ingredients_to_recipe:
                ingredient = ingredient_to_recipe.product
                ingredient_name = ingredient.name
                ingredient_quantity = ingredient_to_recipe.amount
                measurement_unit = ingredient.measurement_unit
                if ingredient_name in ingredient_data:
                    ingredient_data[
                        'ingredient_quantity'] += ingredient_quantity
                else:
                    ingredient_data = {
                        'ingredient_name': ingredient_name,
                        'ingredient_quantity': ingredient_quantity,
                        'measurement_unit': measurement_unit,
                    }
                ingredients.append(ingredient_data)
            final_ingredients[recipe_name] = ingredients
        pdf_converter = JsonToPdf()
        pdf_bytes = pdf_converter.json_transformer(final_ingredients)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="recipe.pdf"'
        return response
