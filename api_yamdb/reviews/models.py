from django.db import models


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
