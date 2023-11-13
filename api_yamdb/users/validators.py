import re

from django.core.exceptions import ValidationError

from reviews.constants import REGEX_USERNAME, USERNAME_ME


def validator_username(value):
    if value == USERNAME_ME:
        raise ValidationError(f'Имя пользователя {value} недопустимо')
    newstr = " ".join(set(re.sub(REGEX_USERNAME, '', value)))
    if newstr:
        raise ValidationError(f'Имя не должно содержать: {newstr}')
    return value
