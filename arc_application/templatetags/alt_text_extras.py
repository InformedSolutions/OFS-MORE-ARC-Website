import inflect
from django import template

register = template.Library()


@register.filter(name='inflect')
def number_to_spatial_ordinal(value):
    """
    Template tag to convert a number to its equivalent spatial ordinal
    For example: my_value = 2; {{ my_value|inflect }} -> "second"
    :param value:
    :return:
    """
    engine = inflect.engine()

    abbreviated = engine.ordinal(value)
    ordinal = engine.number_to_words(abbreviated)

    return ordinal
