from django.db.models import Avg
from rest_framework.filters import OrderingFilter
from django.shortcuts import get_object_or_404
from rest_framework import (filters, mixins, permissions,
                            status, viewsets)
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .permissions import Admin, IsAuthorOrReadOnly, Moderator, ReadOnly
from .filters import CustomFilter
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
    """ Получение кода регистрации для получения токена. """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True): # Условие тут не нужно, то что в скобках и так вернёт 400 код, если что пойдет не так.
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRecieveTokenApiView(APIView):
    """ Получение JWT-токена по коду подтверждения. """

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
    """ Получение информации и измение данных пользователей. """

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

# Для жанра и категории сделать миксин, тогда в дочках останется по две строки.
# Для миксина уже есть файл в api

class GenreViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    ''' Получение списка, создание и удаление жанров. '''

    queryset = Genre.objects.all()
    filter_backends = (filters.SearchFilter,)
    serializer_class = GenreSerializer
    permission_classes = (Admin | ReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """ Получение списка, создание и удаление категорий. """

    queryset = Category.objects.all()
    filter_backends = (filters.SearchFilter,)
    serializer_class = CategorySerializer
    permission_classes = (Admin | ReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """ Получение списка всех объектов. """

    queryset = Title.objects.annotate(
        rating_avg=Avg('reviews__score') # Убрать _avg
    ).order_by('id')
    ''' Никакого прока от сортировки по техническому полю "ключ" нет.
Учти, что значения ключей - это случайные величины (точнее они могут непредсказуемо измениться).
Поэтому сортировка по ним - это опять случайная последовательность объектов.
Лучше заменить на предметное поле (можно на несколько полей - ведь это перечисление)'''
    permission_classes = (Admin | ReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = CustomFilter
    http_method_names = ('get', 'post', 'patch', 'delete')
    # Нужно ограничить сортировку в теле Viewset, см.
    # https://www.django-rest-framework.org/api-guide/filtering/#specifying-which-fields-may-be-ordered-against

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update', 'delete'):
            return CreateTitleSerializer
        return DetailedTitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ Работа с отзывами на произведения. """

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
    """ Работа с комментариями. """

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
