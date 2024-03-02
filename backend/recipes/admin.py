from django.contrib import admin

from .models import (Tag, Product, Recipe,
                     IngredientToRecipe, PurchaseList,
                     Favorite)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        # 'get_recipe_favorites_count',
    )
    list_filter = (
        'author',
        'name',
        'tags'
    )
    # actions = ()

    # def get_recipe_favorites_count(self, obj):
    #     return obj.is_favorited.count()
    # get_recipe_favorites_count.short_description = 'Добавлено в избранное'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Модель ингридиентов с выводом наименования и единицы измерения
    и фильтрацией по наименованию.
    """
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = (
        'name',
    )


admin.site.register(Tag)
admin.site.register(IngredientToRecipe)
admin.site.register(PurchaseList)
admin.site.register(Favorite)
