from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from .views import (
    UserListCreateView,
    UserDetailView,
    SetPasswordView,
    TagsViewSet,
    IngredientViewset,
    FollowListView,
    FollowRetrieveDeleteView,
    FavoriteRetrieveDeleteView,
    ShoppingListRetrieveDeleteView,
    GetShoppingListView,
    RecipeViewSet
)

router = DefaultRouter()
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientViewset, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    re_path(
        r'users/(?P<pk>\d+|me)/$',
        UserDetailView.as_view(),
        name='user-detail'
    ),
    path(
        'users/<int:pk>/subscribe/',
        FollowRetrieveDeleteView.as_view(),
        name='follow-list-create'
    ),
    path(
        'users/subscriptions/',
        FollowListView.as_view(),
        name='subscriptions'
    ),
    path(
        'users/set_password/',
        SetPasswordView.as_view(),
        name='set-password'
    ),
    path(
        'recipes/<int:pk>/favorite/',
        FavoriteRetrieveDeleteView.as_view(),
        name='favorite-recipes'
    ),
    path(
        'recipes/<int:pk>/shopping_cart/',
        ShoppingListRetrieveDeleteView.as_view(),
        name='retrieve-delete-shopping-list'
    ),
    path(
        'recipes/download_shopping_cart/',
        GetShoppingListView.as_view(),
        name='get-shopping-cart'
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
