import re

from django.core.exceptions import ValidationError


def validator_username(value):
    if value == 'me':
        raise ValidationError(f'Имя пользователя {value} недопустимо')
    newstr = re.sub(r'^[\w.@+-]+\Z', '', value) # r'^[\w.@+-]+\Z' Вынести в константу, как и me
                                                # Чтобы не было повторов, лучше использовать set, так же потребуется join, чтобы объединить строку.
    if value in newstr:
        raise ValidationError(f'Имя не должно содержать {newstr}')
    return value
