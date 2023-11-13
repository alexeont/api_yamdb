from django.core.exceptions import ValidationError
from django.utils.timezone import now


def validate_year(value):
    if value > now().year:
        raise ValidationError('Нельзя добавить произведение из будущего')
    return value
