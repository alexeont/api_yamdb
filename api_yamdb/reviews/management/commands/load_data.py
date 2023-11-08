from reviews.import_data import import_data_from_csv

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_data_from_csv()
