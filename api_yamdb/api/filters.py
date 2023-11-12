from django.db.models import Q
import django_filters
from reviews.models import Title


class CustomFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(field_name='genre__slug',
                                      lookup_expr='exact')
    category = django_filters.CharFilter(field_name='category__slug',
                                         lookup_expr='exact')
    name = django_filters.CharFilter(field_name='name', lookup_expr='exact')

    class Meta:
        model = Title
        fields = ['genre', 'category', 'year', 'name']

    def filter_by_genre(self, queryset, name, value):
        return queryset.filter(Q(genre__slug=value))

    def filter_by_category(self, queryset, name, value):
        return queryset.filter(Q(category__slug=value))
