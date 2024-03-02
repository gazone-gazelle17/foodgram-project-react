import os

from django.db import migrations
from rest_framework.utils import json

from recipes.models import Product


def bulk_product_create(_first, _second):
    with open(os.path.join(os.path.dirname(__file__),
                           '..', 'ingredients.json'),
              'r') as file:
        products = json.load(file)
        for product in products:
            Product.objects.create(
                name=product['name'],
                measurement_unit=product['measurement_unit']
            )


class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0002_initial'),
    ]
    operations = [
        migrations.RunPython(bulk_product_create),
    ]
