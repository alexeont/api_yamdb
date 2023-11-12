import re

from django.core.exceptions import ValidationError


def validator_username(value):
    if value == 'me':
        raise ValidationError(f'Имя пользователя {value} недопустимо')
    newstr = re.sub(r'^[\w.@+-]+\Z', '', value)
    if value in newstr:
        raise ValidationError(f'Имя не должно содержать {newstr}')
    return value
