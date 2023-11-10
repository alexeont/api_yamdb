from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

ROLE_CHOICES = (
    ('user', 'Пользователь'),  # Левую часть убрать в константы.
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
    ('superuser', 'Суперюзер'),  # Лишняя строка, супера нужно включать в админа, см. ниже.
)


def validate_username(value): # см. файл
    if value == 'me':
        raise ValidationError("Такое имя пользователя недопустимо")
    return value

'''Общее для всех моделей:
Смотрим редок внимательно и видим там правильное ограничение длинны для всех полей.
Все настройки длины выносим в файл с константами (не settings), для многих полей они будут одинаковыми, не повторяемся.
Для всех полей нужны verbose_name. 
Для всех классов нужны в классах Meta verbose_name.
У всех классов где используется пагинация, должна быть умолчательная сортировка.
Для всех классов нужны методы __str__.'''

class User(AbstractUser):
    """ Класс пользователей. """
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
    email = models.EmailField('E-mail: ', max_length=254,
                              unique=True, null=False)
    first_name = models.CharField('Имя: ', max_length=150, blank=True)
    last_name = models.CharField('Фамилия: ', max_length=150, blank=True)
    role = models.CharField('Роль: ', max_length=9,  # Длину нужно подсчитать прямо тут, подсказка: используем лен и генератор.
                            choices=ROLE_CHOICES, default='user')  # Используем константу, никаких литералов быть не должно.
    bio = models.TextField('Биография: ', blank=True)

    class Meta:
        ordering = ('username',)
    # Используем этот декоратор, чтобы установить 2 новых свойства для модели юсера, - ис_админ и ис_модератор,
    # в админа включаем ис_суперюсер и стафф, а не только роль админа, так мы избавимся от неэффективной проверки в пермишенах.

    def __str__(self):
        return self.username
