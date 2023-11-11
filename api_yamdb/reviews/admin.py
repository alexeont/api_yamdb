from django.contrib import admin
from .models import TitleGenre, Title, Genre, Category, Review


class GenreItemTabular(admin.TabularInline):
    model = TitleGenre


class TitleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name',
                    'year',
                    'description', 'category',]
    list_filter = ['category__name']
    inlines = [
        GenreItemTabular,
    ]
    search_fields = ('name', 'category')


class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ('name',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ('name',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['text', 'score', 'title']
    list_filter = ['score']
    search_fields = ('text', 'title__name')


admin.site.register(Title, TitleAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Review, ReviewAdmin)
