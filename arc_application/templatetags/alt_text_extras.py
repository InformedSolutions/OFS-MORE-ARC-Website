from django import template

from ..utils import spatial_ordinal


register = template.Library()


@register.filter(name='inflect')
def number_to_spatial_ordinal(value):
    """
    Template tag to convert a number to its equivalent spatial ordinal
    For example: my_value = 2; {{ my_value|inflect }} -> "second"
    :param value:
    :return:
    """
    return spatial_ordinal(value)
