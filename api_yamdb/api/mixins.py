
from users.validators import validator_username
from rest_framework import mixins, viewsets, filters
from .permissions import Admin, ReadOnly


class UserMixin: # Не верное имя для mixin, в имени нужно отразить для чего он конкретно нужен.
    def validate_username(self, value):
        return validator_username(value)


class ObjectMixim(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    filter_backends = (filters.SearchFilter,)
    permission_classes = (Admin | ReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'
