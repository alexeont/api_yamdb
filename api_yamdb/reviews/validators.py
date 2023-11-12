from django.core.exceptions import ValidationError
from django.utils.timezone import now

from .constants import MIN_TITLE_YEAR


def validate_year(value):
    if value < MIN_TITLE_YEAR or value > now().year:
        raise ValidationError('Проверьте введенный год произведения')
