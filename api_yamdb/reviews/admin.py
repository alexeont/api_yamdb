from django.contrib import admin
from .models import TitleGenre, Title, Genre, Category, Review


class GenreItemTabular(admin.TabularInline):
    model = TitleGenre


class TitleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name',
                    'year', 'rating',
                    'description', 'category',]
    inlines = [
        GenreItemTabular,

    ]


class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['text', 'score', 'title']


admin.site.register(Title, TitleAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Review, ReviewAdmin)
