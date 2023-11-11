from django.shortcuts import get_object_or_404
from rest_framework import (filters, generics, permissions,
                            status, viewsets)
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .permissions import Admin, IsAuthorOrReadOnly, Moderator, ReadOnly
from .serializers import (CategorySerializer,
                          CommentSerializer,
                          GenreSerializer,
                          RegisterSerializer,
                          ReviewSerializer,
                          UserRecieveTokenSerializer,
                          CreateTitleSerializer,
                          DetailedTitleSerializer,
                          UserSerializer)
from reviews.models import Category, Genre, Review, Title
from users.models import User


''' User Views. '''


class UserRegisterApiView(APIView):
    ''' Получение кода регистрации для получения токена. '''
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRecieveTokenApiView(APIView):
    ''' Получение JWT-токена по коду подтверждения. '''
    queryset = User.objects.all()
    serializer_class = UserRecieveTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserRecieveTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = serializer.validated_data['confirmation_code']
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            return Response('Неверный код', status=status.HTTP_400_BAD_REQUEST)
        message = {'token': str(AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    ''' Получение информации и измение данных пользователей. '''
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (Admin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(methods=['get', 'patch'], detail=False,
            url_path='me', permission_classes=(permissions.IsAuthenticated,))
    def get_me_data(self, request):
        if request.method == 'PATCH':
            serializer = UserSerializer(request.user,
                                        data=request.data,
                                        partial=True,
                                        context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


''' Core Views. '''


class GenreViewSet(generics.ListCreateAPIView):
    ''' Получение списка жанров. '''
    queryset = Genre.objects.all()
    filter_backends = (filters.SearchFilter,)
    serializer_class = GenreSerializer
    permission_classes = (Admin | ReadOnly,)
    search_fields = ('name',)


class GenreDestroyViewSet(generics.DestroyAPIView):
    ''' Удаление жанра. '''
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (Admin, )

    def get_object(self):
        return Genre.objects.get(slug=self.kwargs.get('genre_slug'))


class CategoryViewSet(generics.ListCreateAPIView):
    ''' Получение списка категорий. '''
    queryset = Category.objects.all()
    filter_backends = (filters.SearchFilter,)
    serializer_class = CategorySerializer
    permission_classes = (Admin | ReadOnly,)
    search_fields = ('name',)


class CategoryDestroyViewSet(generics.DestroyAPIView):

    '''По классам выше нужно создать свой ViewSet, нам нужно объединить 3 mixin - создание удаление и получение списка и GenericViewSet.
В него убрать все строки кроме двух, тогда в жанрах и категории будет только по 2 строки и классов будет только 2.'''

    ''' Удаление категории. '''
    queryset = Category.objects.all()
    permission_classes = (Admin,)

    def get_object(self):
        return Category.objects.get(slug=self.kwargs.get('category_slug'))


class FilterBackend(BaseFilterBackend):

    #  Фильтры нужно размещать в соответствующем файле и писать их на основе FilterSet.

    ''' Кастомный фильтр. '''
    def filter_queryset(self, request, queryset, view):
        genre = request.GET.get('genre')
        category = request.GET.get('category')
        if genre:
            return queryset.filter(Q(genre__slug=genre))
        if category:
            queryset = queryset.filter(Q(category__slug=category))
        return queryset


class TitleViewSet(viewsets.ModelViewSet):
    ''' Получение списка всех объектов. '''
    queryset = Title.objects.all()
    #  Тут и прикрутить аннотацию рейтинга по среднему значению score,
    # тогда не нужны будет ни поля в модели, ни методы в сериализаторе,
    # всего одна строка всё решит, тем более что и в запросах будет большой выигрыш.  
    permission_classes = (Admin | ReadOnly,)
    filter_backends = (DjangoFilterBackend,  # Нужно добавить бек сортировки, и ограничить её в теле Viewset
                       FilterBackend)
    filterset_fields = ('name', 'year')
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':  # Использовать проверку вхождения в кортеж.
                                                                        # У нас разрешено удаление.
            return CreateTitleSerializer
        return DetailedTitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    ''' Работа с отзывами на произведения. '''
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly | Admin | Moderator,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    ''' Работа с комментариями. '''
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly | Admin | Moderator,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        review=self.get_review())
