from django.core.management.base import BaseCommand

from reviews.import_data import import_data_from_csv


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_data_from_csv()
