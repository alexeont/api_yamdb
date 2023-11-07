import csv
from reviews.models import Genre, Category


def import_data_from_csv():
    with open('static/data/genre.csv',
              newline='',
              encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Genre.objects.get_or_create(name=row['name'], slug=row['slug'])

    with open('static/data/category.csv',
              newline='',
              encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Category.objects.create(name=row['name'], slug=row['slug'])
