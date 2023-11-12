from django.db.models import Q
import django_filters
from reviews.models import Title


class CustomFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(field_name='genre__slug',
                                      method='filter_by_genre') # Методы тут не нужны, нужно просто прописать lookup_expr и в категории.
    category = django_filters.CharFilter(field_name='category__slug',
                                         method='filter_by_category')
    year = django_filters.NumberFilter(field_name='year', lookup_expr='exact') # Избыточно тут указывать год, достаточно указать его в мете.
    name = django_filters.CharFilter(field_name='name', lookup_expr='exact')

    class Meta:
        model = Title
        fields = ['genre', 'category', 'year', 'name']

    def filter_by_genre(self, queryset, name, value):
        return queryset.filter(Q(genre__slug=value))

    def filter_by_category(self, queryset, name, value):
        return queryset.filter(Q(category__slug=value))
