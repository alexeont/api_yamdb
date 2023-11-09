import csv
from reviews.models import Genre, Category, Title, TitleGenre, Comment, Review
from users.models import User


def import_data_from_csv():

    with open('static/data/users.csv',
              newline='',
              encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            User.objects.get_or_create(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                role=row['role'],
                bio=row['bio'],
                first_name=row['first_name'],
                last_name=row['last_name'],
            )

    with open('static/data/genre.csv',
              newline='',
              encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Genre.objects.get_or_create(
                name=row['name'],
                slug=row['slug']
            )

    with open('static/data/category.csv',
              newline='',
              encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Category.objects.get_or_create(
                name=row['name'],
                slug=row['slug']
            )

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
            TitleGenre.objects.get_or_create(
                title=Title.objects.get(id=int(row['title_id'])),
                genre=Genre.objects.get(id=int(row['genre_id'])),
            )

    with open('static/data/review.csv',
              newline='',
              encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Review.objects.get_or_create(
                text=row['text'],
                score=int(row['score']),
                title=Title.objects.get(id=int(row['title_id'],)),
                pub_date=row['pub_date'],
                author=User.objects.get(id=int(row['author'],))
            )

    with open('static/data/comments.csv',
              newline='',
              encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Comment.objects.get_or_create(
                text=row['text'],
                review=Review.objects.get(id=int(row['review_id'])),
                pub_date=row['pub_date'],
                author=User.objects.get(id=int(row['author'],))
            )

