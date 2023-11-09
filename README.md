## Проект «API для Yatube»

### Описание:

Учебный проект для отработки на практике различных способов детальной настройки собственного API-сервиса.

### Стек:

```
Python 3.9 as programming language
```

```
Django 3.2 as web framework

```

```
Django REST framework 3.12 as toolkit for building Web APIs
```

```
SQLite3 as database
```

```
djoser 2.1 as library for authentication
```

```
GitHub as repo and workflows manager
```

### Установка:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/aleksey-vasilev/api_final_yatube
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

### Примеры запросов:

#### Создание публикации:

```
POST /api/v1/posts/
```
json
{

    "text": "string",
    "image": "string",
    "group": 0

}

#### Пример ответа:

json
{

    "id": 0,
    "author": "string",
    "text": "string",
    "pub_date": "2019-08-24T14:15:22Z",
    "image": "string",
    "group": 0

}

#### Получение комментария:

```
GET /api/v1/posts/{post_id}/comments/{id}/
```
#### Пример ответа:

json
{

    "id": 0,
    "author": "string",
    "text": "string",
    "created": "2019-08-24T14:15:22Z",
    "post": 0

}
