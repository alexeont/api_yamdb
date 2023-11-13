from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from rest_framework.filters import OrderingFilter
from django.shortcuts import get_object_or_404
from rest_framework import (filters, permissions,
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
from .mixins import ObjectMixim
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
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.get(**serializer.validated_data)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Ваш код регистрации',
            message=(f'Код регистрации для {user.username}: '
                     f'{confirmation_code}'),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class GenreViewSet(ObjectMixim):
    ''' Получение списка, создание и удаление жанров. '''

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(ObjectMixim):
    """ Получение списка, создание и удаление категорий. """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    """ Получение списка всех объектов. """

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('name', '-year')
    permission_classes = (Admin | ReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = CustomFilter
    http_method_names = ('get', 'post', 'patch', 'delete')
    ordering_fields = ['name', 'year']

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
