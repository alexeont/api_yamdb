from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User

admin.site.empty_value_display = 'Не задано'


@admin.register(User)
class UserAdmin(admin.ModelAdmin): # admin.ModelAdmin Не подходит для модели User, нужно использовать
                                   # UserAdmin из django.contrib.auth.admin, можно импортировать его как as BaseUserAdmin.
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'bio', 'role',
                    'reviews_count')
    list_editable = ('role',)
    list_filter = ('username',)
    search_fields = ('username', 'email', 'role')

    @admin.display(description='Обзоры')
    def reviews_count(self, obj):
        return obj.reviews.count()


admin.site.unregister(Group)
admin.site.site_title = 'Администрирование «YaMDb»'
admin.site.site_header = 'Администрирование «YaMDb»'
