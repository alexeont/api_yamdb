from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    '''Для классов Регистрации и Проверки токена не нужно общение с БД, нужно переопределить родительский класс.
Так же смотри замечание в модели про валидацию и про длину полей, это касается всех сериалайзеров для Пользователя.'''

    class Meta:
        model = User
        fields = (
            'username', 'email'
        )

    def validate(self, data):
        if data.get('username') == 'me': # Этого мало, нужна проверка на регулярку, см. в модели.
                                         # Тоже самое для всех сериализаторов пользователя.
            raise serializers.ValidationError('Недопустимое имя пользователя')
        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError('Такой e-mail уже есть')
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError('Такой пользователь уже есть')
        return data


class UserRecieveTokenSerializer(serializers.Serializer):
    username = serializers.RegexField(regex=r'^[\w.@+-]+$',
                                      max_length=150,
                                      required=True)
    confirmation_code = serializers.CharField(max_length=254,
                                              required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError('Недопустимое имя пользователя')
        return username


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
