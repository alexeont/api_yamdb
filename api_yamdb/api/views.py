from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import (filters, generics, mixins, permissions,
                            status, viewsets)
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend

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


class UserViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
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
    permission_classes = (Admin, )

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


class FilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        genre = request.GET.get('genre')
        category = request.GET.get('category')
        if genre:
            return queryset.filter(Q(genre__slug=genre))
        if category:
            queryset = queryset.filter(Q(category__slug=category))
        return queryset


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (Admin | ReadOnly,)
    filter_backends = (DjangoFilterBackend,
                       FilterBackend)
    filterset_fields = ('name', 'year')
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'patch':
            return CreateTitleSerializer
        return DetailedTitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly | Admin | Moderator,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def update_title_rating(self, title):
        reviews = self.get_queryset()
        total_score = sum(review.score for review in reviews)
        average_rating = total_score / reviews.count()
        title.rating = round(average_rating, 1)
        title.save()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        title=self.get_title())

    def perform_update(self, serializer):
        serializer.save()
        title = serializer.instance.title
        self.update_title_rating(title)

    def perform_destroy(self, instance):
        title = instance.title
        instance.delete()
        self.update_title_rating(title)


class CommentViewSet(viewsets.ModelViewSet):
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
