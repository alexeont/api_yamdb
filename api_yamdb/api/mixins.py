
from users.validators import validator_username


class UsernameVilidatorMixin:
    def validate_username(self, value):
        return validator_username(value)
