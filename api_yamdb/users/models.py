from django.contrib.auth.models import AbstractUser
from django.db import models

from reviews.constants import (ADMIN, MODERATOR, USER,
                               MAX_USERNAME_CHARACTERS, MAX_EMAIL_CHARACTERS)
from .validators import validator_username

ROLE_CHOICES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор')
)


class User(AbstractUser):
    """ Класс пользователей. """
    username = models.CharField(
        'Логин',
        max_length=MAX_USERNAME_CHARACTERS,
        unique=True,
        help_text=('Обязательное поле. Не более 150 символов. '
                   'Только буквы и цифры, символы @+-'),
        validators=[validator_username, ],
        error_messages={
            'unique': 'Пользователь с таким именем уже есть',
        }
    )
    email = models.EmailField('E-mail: ', max_length=MAX_EMAIL_CHARACTERS,
                              unique=True, null=False) # null=False Является значением по умолчанию, значения по умолчанию писать не нужно.
    first_name = models.CharField('Имя: ',
                                  max_length=MAX_USERNAME_CHARACTERS,
                                  blank=True)
    last_name = models.CharField('Фамилия: ',
                                 max_length=MAX_USERNAME_CHARACTERS,
                                 blank=True)
    role = models.CharField('Роль: ',
                            max_length=max([len(i[0]) for i in ROLE_CHOICES]),
                            choices=ROLE_CHOICES, default=USER) # Избавиться от индексов, распаковывать 2 переменные, если какая то переменная не используется ей принято не давать имени, а записать так - _.
                                                                # Не допустимо использовать однобуквенные переменные.
    bio = models.TextField('Биография: ', blank=True)

    @property
    def is_admin(self):
        return (self.role == ADMIN
                or self.is_superuser
                or self.is_staff)

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        verbose_name = "Пользователь" # Не консистентные кавычки.
                                      # Все кавычки в файле должны быть одного типа, кроме вложенных (у докстрингс кавычки всегда двойные).
        verbose_name_plural = "Пользователи"
        ordering = ('username',)

    def __str__(self):
        return self.username
