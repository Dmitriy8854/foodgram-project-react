from csv import DictReader

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Загрузка данных из ingredients.csv в Ingredient:")
        model = Ingredient
        if model.objects.exists():
            print(
                f"{model.name} заполнена другими данными, отменена загрузки"
            )
        else:
            for row in DictReader(
                open("data/ingredients.csv", encoding="utf8")
            ):
                model.objects.create(
                    tittle=row["ingredient"],
                    measurement=row["measurement"]
                )
        print("Загрузка завершена")
