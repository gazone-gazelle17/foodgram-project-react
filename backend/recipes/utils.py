from .models import Ingredient


def update_purchase_list_totals(purchase_list):

    recipes = purchase_list.recipes.all()
    total_quantities = {}

    for recipe in recipes:
        ingredients = Ingredient.objects.filter(recipe=recipe)
# ниже внимательно переделать!
        for ingredient in ingredients:
            if ingredient not in total_quantities.keys:
                # то добавляем ингредиент в словарь в качестве ключа, а потом в значении на каждой итерации прибавляем количество
            total_quantities.setdefault(ingredient.product, 0)
            total_quantities[ingredient.product] += ingredient.quantity

    for product, total_quantity in total_quantities.items():
        purchase_list.total_quantity += total_quantity
    purchase_list.save()
