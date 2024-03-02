from django.contrib.auth import get_user_model
from django.db import models
from autoslug import AutoSlugField
from colorfield.fields import ColorField

User = get_user_model()


class Tag(models.Model):
    """Модель тега для поиска рецептов."""

    COLOR_PALETTE = [
        ('#FF0000', 'red'),
        ('#FFC0CB', 'pink'),
        ('#FFA500', 'orange'),
        ('#FFFF00', 'yellow'),
        ('#800080', 'purple'),
        ('#FFFFFF', 'white'),
        ('#808080', 'gray'),
        ('#00FF00', 'lime'),
    ]

    name = models.CharField(max_length=16, verbose_name='Наименование')
    color = ColorField(max_length=7, samples=COLOR_PALETTE,
                       verbose_name='Цвет тега')
    slug = AutoSlugField(populate_from='name', unique=True,
                         verbose_name='Слаг тега')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']
        unique_together = ['name', 'color', 'slug']

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Модель отдельно взятого продукта.
    Важное замечание: под продуктом понимается именно продукт,
    не включенный в рецепт.
    """

    name = models.CharField(max_length=255, verbose_name='Наименование')
    measurement_unit = models.CharField(max_length=255,
                                        verbose_name='Единица измерения')

    class Meta:
        ordering = ['name']
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель отдельно взятого рецепта."""

    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    author = models.ForeignKey(User, related_name='recipes',
                               on_delete=models.CASCADE, verbose_name='Автор')
    ingredients = models.ManyToManyField(Product, through='IngredientToRecipe',
                                         verbose_name='Ингредиент')
    name = models.CharField(max_length=26, verbose_name='Наименование')
    image = models.ImageField(
        upload_to='recipes/images/',
        default=None,
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class IngredientToRecipe(models.Model):
    """
    Модель отдельно взятого ингредиента.
    Важное замечание: под ингредиентом понимается продукт, включенный в рецепт.
    """

    recipe = models.ForeignKey(Recipe, related_name='ingredientsincide',
                               on_delete=models.CASCADE, verbose_name='Рецепт')
    product = models.ForeignKey(Product, related_name='products',
                                on_delete=models.CASCADE,
                                verbose_name='Продукт')
    amount = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['recipe']

    def __str__(self):
        return self.product.name


class PurchaseList(models.Model):
    """Модель списка рецептов с полем total_quantity."""

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='added_to_cart')
    recipe = models.ForeignKey('Recipe',
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='is_in_shopping_cart')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ['recipe']

    def __str__(self):
        return self.recipe.name


class Favorite(models.Model):
    '''Модель избранных рецептов.'''

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='favorites')
    recipe = models.ForeignKey('Recipe',
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='is_favorited')

    class Meta:
        ordering = ['author']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = [['author', 'recipe']]

    def __str__(self):
        return self.author.username
