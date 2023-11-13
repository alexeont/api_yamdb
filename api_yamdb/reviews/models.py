from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (MAX_NAME_CHARS,
                        MAX_SCORE_VALUE,
                        MAX_SLUG_CHARS,
                        MIN_SCORE_VALUE,
                        SCORE_VALIDATION_MESSAGE,
                        TRUNCATED_MODEL_NAME,)
from .validators import validate_year
from users.models import User


class NameSlugModel(models.Model):
    """ Базовый класс для Жанра и Категории. """

    name = models.CharField('Название',
                            max_length=MAX_NAME_CHARS)
    slug = models.SlugField('Слаг',
                            max_length=MAX_SLUG_CHARS,
                            unique=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:TRUNCATED_MODEL_NAME]


class AuthorTextPubdateModel(models.Model):
    """ Базовый класс для Ревью и Коммента. """

    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор')
    text = models.TextField('Текст')

    class Meta:
        abstract = True
        ordering = ('pub_date',)

    def __str__(self):
        return self.text[:TRUNCATED_MODEL_NAME]


class Genre(NameSlugModel):
    """ Жанры произведений. """

    class Meta(NameSlugModel.Meta):
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Category(NameSlugModel):
    """ Категории (типы) произведений. """

    class Meta(NameSlugModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    """ Произведения, к которым пишут отзывы. """

    name = models.CharField('Название произведения',
                            max_length=MAX_NAME_CHARS)
    year = models.SmallIntegerField('Год', db_index=True,
                                    validators=(validate_year,))
    description = models.TextField('Описание', blank=True, null=True)
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre',
        related_name='title_genre',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='title_category',
        null=True,
        verbose_name='Категория'
    )

    class Meta:
        ordering = ('year',)
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:TRUNCATED_MODEL_NAME]


class TitleGenre(models.Model):
    """ Промежуточная таблица для связи произведений и жанров. """

    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              verbose_name='Название произведения')
    genre = models.ForeignKey(Genre,
                              on_delete=models.CASCADE,
                              verbose_name='Жанр')

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(AuthorTextPubdateModel):
    """ Отзыв на Тайтл. """

    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              verbose_name='Отзыв на: ')
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=(
            MaxValueValidator(
                MAX_SCORE_VALUE, message=SCORE_VALIDATION_MESSAGE),
            MinValueValidator(
                MIN_SCORE_VALUE, message=SCORE_VALIDATION_MESSAGE))
    )

    class Meta(AuthorTextPubdateModel.Meta):
        default_related_name = 'reviews'
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('author_id', 'title_id'),
                name='unique_review'
            )
        ]


class Comment(AuthorTextPubdateModel):
    """ Комментарий на отзыв. """

    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               verbose_name='Комментарий к: ')

    class Meta(AuthorTextPubdateModel.Meta):
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
