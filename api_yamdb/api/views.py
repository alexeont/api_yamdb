from django.core.mail import send_mail
from django.db.models import Avg
from rest_framework.filters import OrderingFilter
from django.shortcuts import get_object_or_404
from rest_framework import (filters, generics, mixins, permissions,
                            status, viewsets)
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend

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


class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):  # Избыточный родитель, тут хватит либо APIView либо вообще функции с декоратором @api_view.
                                                                          # То же самое для класса получения токена.
    ''' Отправка письма с кодом регистрации для получения токена. '''
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        if not User.objects.filter(username=request.data.get('username'),  # Вся валидация должна быть в сериализаторе.
                                   email=request.data.get('email')).exists():
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = User.objects.create(**serializer.validated_data)  # Создавать пользователя лучше в сериализаторе в методе create
        else:
            user = User.objects.get(username=request.data.get('username'))
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Ваш код регистрации',
            message=(f'Код регистрации для {request.data.get("username")}: '
                     f'{confirmation_code}'),
                    from_email='domashkapraktikum@yandex.ru',  # Это есть в settings.
                    recipient_list=[request.data.get('email')],
                    fail_silently=True,)
        return Response(request.data, status=status.HTTP_200_OK)


class UserRecieveTokenViewSet(mixins.CreateModelMixin,
                              viewsets.GenericViewSet):
    ''' Получение JWT-токена по коду подтверждения. '''
    queryset = User.objects.all()
    serializer_class = UserRecieveTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serializer = UserRecieveTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = serializer.validated_data['confirmation_code']
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            return Response('Неверный код', status=status.HTTP_400_BAD_REQUEST)
        message = {'token': str(AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)


class UserViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,  # Тут нужен ModelViewSet, просто ограничить метод put в теле ViewSet.
                  viewsets.GenericViewSet):
    ''' Получение информации и измение данных пользователей. '''
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (Admin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

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

    @action(methods=['get', 'patch', 'delete'], detail=False,
            url_path=r'(?P<username>[\w.@+-]+)')
    def get_user_by_username(self, request, username):  # Лишний метод, в полном ViewSet он будет не нужен.
        user = get_object_or_404(User, username=username)
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


''' Core Views. '''


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
    ''' Получение списка, создание и удаление жанров. '''

    queryset = Category.objects.all()
    filter_backends = (filters.SearchFilter,)
    serializer_class = CategorySerializer
    permission_classes = (Admin | ReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    ''' Получение списка всех объектов. '''
    queryset = Title.objects.annotate(
        rating_avg=Avg('reviews__score')
    ).order_by('id')
    permission_classes = (Admin | ReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = CustomFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update', 'delete'):
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
