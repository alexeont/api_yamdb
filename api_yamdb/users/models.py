from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

ROLE_CHOICES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
    ('superuser', 'Суперюзер'),
)


def validate_username(value):
    if value == 'me':
        raise ValidationError("Такое имя пользователя недопустимо")
    return value


class User(AbstractUser):

    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        help_text=('Обязательное поле. Не более 150 символов. '
                   'Только буквы и цифры, символы @+-'),
        validators=[validate_username,
                    RegexValidator(r'^[\w.@+-]+\Z',
                                   'Используются недопустимые символы')],
        error_messages={
            'unique': 'Пользователь с таким именем уже есть',
        }
    )
    email = models.EmailField('E-mail: ', max_length=254, null=False)
    first_name = models.CharField('Имя: ', max_length=150, blank=True)
    last_name = models.CharField('Фамилия: ', max_length=150, blank=True)
    role = models.CharField('Роль: ', max_length=9,
                            choices=ROLE_CHOICES, default='user')
    bio = models.TextField('Биография: ', blank=True)

    def __str__(self):
        return self.username
