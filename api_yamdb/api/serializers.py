from django.db import IntegrityError
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.constants import MIN_SCORE_VALUE, MAX_SCORE_VALUE
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
    rating = serializers.FloatField(source='rating_avg',
                                    read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'rating', 'category', 'genre')


class CreateTitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                            slug_field='slug')
    genre = serializers.SlugRelatedField(queryset=Genre.objects.all(),
                                         many=True,
                                         slug_field='slug')

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError("Genre list cannot be empty.")
        return value

    def to_representation(self, instance):
        serializer = DetailedTitleSerializer(instance)
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True,
                              default=serializers.CurrentUserDefault())
    score = serializers.IntegerField(max_value=MAX_SCORE_VALUE,
                                     min_value=MIN_SCORE_VALUE)

    class Meta:
        fields = '__all__'
        model = Review
        extra_kwargs = { # Так может не сработать
            'score':
            {'error_messages':
                {'max_value': ('Нельзя поставить больше десятки'),
                 'min_value': ('Нельзя поставить меньше единицы')}}
        }

    def validate(self, data):
        if self.context['request'].method == 'POST':
            author_id = self.context['request'].user.id
            title_id = self.context['view'].kwargs.get('title_id')
            review = Review.objects.filter(author_id=author_id,
                                           title_id=title_id)
            if review.exists():
                raise serializers.ValidationError(
                    'Неуникальная пара Автор-Отзыв')
            return data


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('review',)
