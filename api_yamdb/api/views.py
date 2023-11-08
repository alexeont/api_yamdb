from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import (filters, generics, mixins, permissions,
                            status, viewsets)
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import Admin, IsAuthorOrReadOnly, Moderator, ReadOnly
from .serializers import (CategorySerializer,
                          CommentSerializer,
                          GenreSerializer,
                          RegisterSerializer,
                          ReviewSerializer,
                          TitleSerializer,
                          UserRecieveTokenSerializer,
                          UserSerializer)
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

''' User Views. '''


class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        if not User.objects.filter(username=request.data.get('username'),
                                   email=request.data.get('email')).exists():
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = User.objects.create(**serializer.validated_data)
        else:
            user = User.objects.get(username=request.data.get('username'))
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Ваш код регистрации',
            message=(f'Код регистрации для {request.data.get("username")}: '
                     f'{confirmation_code}'),
                    from_email='domashkapraktikum@yandex.ru',
                    recipient_list=[request.data.get('email')],
                    fail_silently=True,)
        return Response(request.data, status=status.HTTP_200_OK)


class UserRecieveTokenViewSet(mixins.CreateModelMixin,
                              viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserRecieveTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = UserRecieveTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = serializer.validated_data['confirmation_code']
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            return Response('Неверный код', status=status.HTTP_400_BAD_REQUEST)
        message = {'token': str(AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)


class UserViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (Admin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            url_name='me', permission_classes=(permissions.IsAuthenticated,))
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

    @action(detail=False, methods=['get', 'patch', 'delete'],
            url_path=r'(?P<username>[\w.@+-]+)', url_name='user')
    def get_user_by_username(self, request, username):
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


class GenreViewSet(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    filter_backends = (filters.SearchFilter,)
    serializer_class = GenreSerializer
    permission_classes = (Admin | ReadOnly,)
    search_fields = ('name',)


class GenreDestroyViewSet(generics.DestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (Admin,)

    def get_object(self):
        return Genre.objects.get(slug=self.kwargs.get('genre_slug'))


class CategoryViewSet(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    filter_backends = (filters.SearchFilter,)
    serializer_class = CategorySerializer
    permission_classes = (Admin | ReadOnly,)
    search_fields = ('name',)


class CategoryDestroyViewSet(generics.DestroyAPIView):
    queryset = Category.objects.all()
    permission_classes = (Admin,)

    def get_object(self):
        return Category.objects.get(slug=self.kwargs.get('category_slug'))


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (Admin | ReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly | Admin | Moderator,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly | Admin | Moderator,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
