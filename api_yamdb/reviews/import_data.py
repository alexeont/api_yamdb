import csv
from reviews.models import Genre, Category, Title, TitleGenre, Comment, Review
from users.models import User


models_dict = {
    'users': User,
    'genre': Genre,
    'category': Category,
    'titles': Title,
    'genre_title': TitleGenre,
    'review': Review,
    'comments': Comment,
}

related_fields = {
    'titles': {'category': Category},
    'review': {'author': User},
    'comments': {'author': User},
}


def import_data_from_csv():
    for file_name, model in models_dict.items():
        with open(f'static/data/{file_name}.csv', newline='',
                  encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                obj_data = {key: value for key, value in row.items()}
                for field, related_model in related_fields.get(
                    file_name, {}
                ).items():
                    obj_data[field] = related_model.objects.get(
                        id=int(row[field])
                    )

                model.objects.get_or_create(**obj_data)