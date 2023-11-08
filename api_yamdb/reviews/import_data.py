import csv
from reviews.models import Genre, Category, Title
from django.db import connection


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
            Category.objects.get_or_create(name=row['name'], slug=row['slug'])

    with open('static/data/titles.csv',
              newline='',
              encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Title.objects.get_or_create(
                name=row['name'],
                year=int(row['year']),
                category=Category.objects.get(id=int(row['category'])),
            )

    with open('static/data/genre_title.csv',
              newline='',
              encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            title_id = int(row['title_id'])
            genre_id = int(row['genre_id'])
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO reviews_title_genre'
                        f'(title_id,genre_id) VALUES ({title_id}, {genre_id})'
                    )

            except Exception as e:
                print(f'Error: {e}')

    # with open('static/data/comments.csv',
    #           newline='',
    #           encoding='utf-8') as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     # for row in reader:
    #     #     Comment.objects.get_or_create(
    #     #         #атрибуты комментария
    #     #     )

    # with open('static/data/review.csv',
    #           newline='',
    #           encoding='utf-8') as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     # for row in reader:
    #     #     Review.objects.get_or_create(
    #     #         #атрибуты ревью
    #     #     )

    # with open('static/data/users.csv',
    #           newline='',
    #           encoding='utf-8') as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     # for row in reader:
    #     #     Title.objects.get_or_create(
    #     #         #атрибуты юзера
    #     #     )
