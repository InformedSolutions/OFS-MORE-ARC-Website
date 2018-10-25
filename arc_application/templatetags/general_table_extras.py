from django import template
from pydoc import locate


register = template.Library()


@register.filter
def template_is_instance(value, arg):
    '''
    :param value: The obj to check the type of.
    :param arg: A type name cast as a string within the template.
    :return: boolean True if obj is of type arg.
    '''
    return isinstance(value, locate(arg))


@register.filter(name='template_string_in_list')
def template_string_in_list(value, arg):
    arg_list = arg.split()
    return value in arg_list


@register.filter
def return_item_by_index(_list, index):
    return _list[index]
