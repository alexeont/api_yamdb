## Проект «YaMDb»

### Описание:

Проект YaMDb собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка».

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
GitHub as repo and workflows manager
```

### Установка:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/alexeont/api_yamdb

```

```
cd api_yamdb
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

Загрузить данные из CSV:

```
python3 manage.py load_data
```

Запустить проект:

```
python3 manage.py runserver
```

### Алгоритм регистрации пользователей

1. Пользователь отправляет POST-запрос на добавление нового пользователя с параметрами `email` и `username` на эндпоинт `/api/v1/auth/signup/`.
2. **YaMDB** отправляет письмо с кодом подтверждения (`confirmation_code`) на адрес  `email`.
3. Пользователь отправляет POST-запрос с параметрами `username` и `confirmation_code` на эндпоинт `/api/v1/auth/token/`, в ответе на запрос ему приходит `token` (JWT-токен).
4. При желании пользователь отправляет PATCH-запрос на эндпоинт `/api/v1/users/me/` и заполняет поля в своём профайле (описание полей — в документации).

### Документация:

Документация API доступна по адресу: http://127.0.0.1:8000/redoc/. 
