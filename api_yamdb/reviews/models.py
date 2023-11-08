from django.db import models

from .constants import (MAX_REVIEW_CHARACTERS,
                        MAX_COMMENT_CHARACTERS,
                        TRUNCATED_MODEL_NAME)


class BaseModel(models.Model):
    """ Базовый класс для Ревью и Коммента. """
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    #author = models.ForeignKey(User, on_delete=models.CASCADE) # Custom User

    class Meta:
        abstract = True


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    rating = models.FloatField(default=0.0)
    description = models.TextField(blank=True, null=True)
    genre = models.ManyToManyField(
        Genre,
        related_name='title_genre',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='title_category',
        null=True
    )

    def __str__(self):
        self.genre

 class Review(BaseModel):
    """ Отзыв на тайтл. """
    #title = models.ForeignKey(Title, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()
    text = models.TextField(max_length=MAX_REVIEW_CHARACTERS)

    class Meta:
        default_related_name = 'reviews'

    def __str__(self):
        return self.text[:TRUNCATED_MODEL_NAME]


class Comment(BaseModel):
    """ Комментарий на отзыв. """
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    text = models.TextField(max_length=MAX_COMMENT_CHARACTERS)

    class Meta:
        default_related_name = 'comments'

    def __str__(self):
        return self.text[:TRUNCATED_MODEL_NAME]