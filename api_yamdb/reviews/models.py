from django.db import models

from .constants import (MAX_REVIEW_CHARACTERS,
                        MAX_COMMENT_CHARACTERS,
                        TRUNCATED_MODEL_NAME)
from users.models import User


class BaseModel(models.Model):
    """ Базовый класс для Ревью и Коммента. """
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор')

    class Meta:
        abstract = True


class Genre(models.Model):
    """ Жанры произведений. """
    name = models.CharField(max_length=256, verbose_name='Навзание')
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name[:TRUNCATED_MODEL_NAME]

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(models.Model):
    """ Категории (типы) произведений. """
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name[:TRUNCATED_MODEL_NAME]

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    """ Произведения, к которым пишут отзывы. """
    name = models.CharField(max_length=256,
                            verbose_name='Название произведения')
    year = models.IntegerField(verbose_name='Год')
    rating = models.FloatField(null=True,
                               blank=True,
                               verbose_name='Рейтинг')
    description = models.TextField(blank=True,
                                   null=True,
                                   verbose_name='Описание')
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre',
        related_name='title_genre',
        verbose_name='Жанры'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='title_category',
        null=True,
        verbose_name='Категории'
    )

    def __str__(self):
        return self.name[:TRUNCATED_MODEL_NAME]

    class Meta:
        ordering = ('year',)
        verbose_name = 'Приозведение'
        verbose_name_plural = 'Произведения'


class TitleGenre(models.Model):
    """ Промежуточная таблица для связи произведений и жанров. """
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(BaseModel):
    """ Отзыв на тайтл. """
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              verbose_name='Название')
    score = models.PositiveSmallIntegerField(verbose_name='Оценка')
    text = models.TextField(max_length=MAX_REVIEW_CHARACTERS,
                            verbose_name='Текст отзыва')

    class Meta:
        default_related_name = 'reviews'
        ordering = ('pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author_id', 'title_id'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return self.text[:TRUNCATED_MODEL_NAME]


class Comment(BaseModel):
    """ Комментарий на отзыв. """
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    text = models.TextField(max_length=MAX_COMMENT_CHARACTERS)

    class Meta:
        default_related_name = 'comments'
        ordering = ('pub_date',)

    def __str__(self):
        return self.text[:TRUNCATED_MODEL_NAME]
