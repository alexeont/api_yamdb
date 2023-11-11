from django.db import IntegrityError
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title
from reviews.constants import (MAX_USERNAME_CHARACTERS, MAX_EMAIL_CHARACTERS,
                               MAX_CODE_CHARACTERS)
from users.models import User
from .mixins import UserMixin


class RegisterSerializer(UserMixin, serializers.Serializer):
    username = serializers.CharField(max_length=MAX_USERNAME_CHARACTERS,
                                     required=True,)
    email = serializers.EmailField(max_length=MAX_EMAIL_CHARACTERS,
                                   required=True)

    def create(self, validated_data):
        try:
            username = validated_data.get('username')
            email = validated_data.get('email')
            user, create = User.objects.get_or_create(username=username,
                                                      email=email)
        except IntegrityError:
            raise serializers.ValidationError(
                'Пользователь с такими данными уже существует'
            )

        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Ваш код регистрации',
            message=(f'Код регистрации для {username}: '
                     f'{confirmation_code}'),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,)
        return user


class UserRecieveTokenSerializer(UserMixin, serializers.Serializer):
    username = serializers.CharField(max_length=MAX_USERNAME_CHARACTERS,
                                     required=True)
    confirmation_code = serializers.CharField(max_length=MAX_CODE_CHARACTERS,
                                              required=True)


class UserSerializer(UserMixin, serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class DetailedTitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'category', 'genre')

    def get_rating(self, obj):
        reviews = Review.objects.filter(title=obj.id)
        if reviews:
            total_score = sum(review.score for review in reviews)
            return total_score / len(reviews)
        return None


class CreateTitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                            slug_field='slug')
    genre = serializers.SlugRelatedField(queryset=Genre.objects.all(),
                                         many=True,
                                         slug_field='slug')

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')
        read_only_fields = ('rating',)
    
    '''Так у нас вывод информации после Пост запроса будет не по ТЗ,
    нужно добавить сюда метод который позволит выводить информацию как при гет запросе.
    Не путаем нужно написать всего один метод.
    Нужна валидация поля Жанра, у нас по ТЗ это поля обязательное, если сейчас
    передать пустой список через Postman, то Произведение создастся вообще без Жанров'''


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True,
                              default=serializers.CurrentUserDefault())
    score = serializers.IntegerField(max_value=10, min_value=1)
    title = serializers.PrimaryKeyRelatedField(queryset=Title.objects.all(),
                                               default=None)

    class Meta:
        fields = '__all__'
        model = Review

    def validate(self, data):
        author_id = self.context['request'].user.id
        title_id = self.context['view'].kwargs.get('title_id')
        review = Review.objects.filter(author_id=author_id, title_id=title_id)
        if self.context['request'].method == 'POST' and review.exists():
            raise serializers.ValidationError(
                'Неуникальная пара Автор-Отзыв')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('review',)
