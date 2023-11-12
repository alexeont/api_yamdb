
from users.validators import validator_username


class UserMixin: # Не верное имя для mixin, в имени нужно отразить для чего он конкретно нужен.
    def validate_username(self, value):
        return validator_username(value)
