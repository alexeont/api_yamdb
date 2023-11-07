from rest_framework import viewsets, generics, filters
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Genre, Category, Title
from .serializers import GenreSerializer, CategorySerializer, TitleSerializer


class GenreViewSet(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    filter_backends = (filters.SearchFilter,)
    serializer_class = GenreSerializer
    search_fields = ('name',)


class GenreDestroyViewSet(generics.DestroyAPIView):
    queryset = Genre.objects.all()
    filter_backends = (filters.SearchFilter,)
    serializer_class = GenreSerializer
    search_fields = ('name',)

    def get_object(self):
        return Genre.objects.get(slug=self.kwargs.get('genre_slug'))


class CategoryViewSet(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDestroyViewSet(generics.DestroyAPIView):
    queryset = Category.objects.all()

    def get_object(self):
        return Category.objects.get(slug=self.kwargs.get('category_slug'))


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')
