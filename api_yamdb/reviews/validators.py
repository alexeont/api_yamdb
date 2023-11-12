from django.core.exceptions import ValidationError
from django.utils.timezone import now


def validate_year(value):
    if value > now().year:
        raise ValidationError('Нельзя добавить произведение из будущего')


def validate_score(value):
    if value < 1 or value > 10:
        raise ValidationError('Введите оценку от 1 до 10')
