import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из CSV'

    def handle(self, *args, **kwargs):
        with open('ingredients.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.create(
                    name=name, measurement_unit=measurement_unit
                )
        self.stdout.write(self.style.SUCCESS(
            'Ингредиенты успешно импортированы!'))
