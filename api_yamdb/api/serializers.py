from rest_framework import serializers

from users.models import User
from reviews.models import Genre, Category, Title


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email'
        )

    def validate(self, data):
        if data.get('username') == 'me':
            raise serializers.ValidationError('Недопустимое имя пользователя')
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

    def validate_role(self, role):
        if self.instance.role != 'admin':
            return self.instance.role
        return role


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField()

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField()

    class Meta:
        fields = ('name', 'slug')
        model = Category


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(queryset=Genre.objects.all(),
                                         many=True,
                                         slug_field='slug')
    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                            slug_field='slug')

    class Meta:
        fields = ('id', 'name', 'year', 'raiting',
                  'description', 'category', 'genre')
        model = Title
        read_only_fields = ('rating',)

      
