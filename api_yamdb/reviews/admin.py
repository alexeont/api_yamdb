from django.contrib import admin

from .models import TitleGenre, Title, Genre, Category, Review


class GenreItemTabular(admin.TabularInline):
    model = TitleGenre


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',
                    'year', 'description',
                    'category', 'display_genres')
    list_filter = ('category__name',)

    @admin.display(description='Жанры')
    def display_genres(self, obj):
        return ', '.join([genre.name for genre in obj.genres.all()])

    inlines = [
        GenreItemTabular,
    ]
    search_fields = ('name', 'category')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('text', 'score', 'title')
    list_filter = ('score',)
    search_fields = ('text', 'title__name')
