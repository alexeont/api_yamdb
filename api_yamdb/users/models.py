from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validator_username
from reviews.constants import (ADMIN, MODERATOR, USER,
                               MAX_USERNAME_CHARACTERS, MAX_EMAIL_CHARACTERS)

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
        validators=(validator_username,),
        error_messages={
            'unique': 'Пользователь с таким именем уже есть',
        }
    )
    email = models.EmailField('E-mail: ', max_length=MAX_EMAIL_CHARACTERS,
                              unique=True)
    first_name = models.CharField('Имя: ',
                                  max_length=MAX_USERNAME_CHARACTERS,
                                  blank=True)
    last_name = models.CharField('Фамилия: ',
                                 max_length=MAX_USERNAME_CHARACTERS,
                                 blank=True)
    role = models.CharField('Роль: ',
                            max_length=max([len(role)
                                            for role, _ in ROLE_CHOICES]),
                            choices=ROLE_CHOICES, default=USER)
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
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username
