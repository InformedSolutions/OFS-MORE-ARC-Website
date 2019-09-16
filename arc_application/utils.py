import inflect

from django.contrib.auth.models import Group


inflect_engine = inflect.engine()


def has_group(user, group_name):
    """
    Check if user is in group
    :return: True if user is in group, else false
    """
    group = Group.objects.get(name=group_name)

    return True if group in user.groups.all() else False


def spatial_ordinal(value):
    """
    Returns the word representing the spatial ordinal for the given value e.g. 2 -> "second"
    """
    return inflect_engine.number_to_words(inflect_engine.ordinal(int(value)))

def get_title_data(dict):
    """
    Function to determine if title is one of the options or an 'other' title
    :param details_dict: dictionary of the adult/applicant's  details
    :return: a dictionary with the title and other_title set correctly
    """
    title = dict['title']
    if title not in TITLE_OPTIONS:
        dict['title'] = 'Other'
        dict['other_title']=title
    else:
        dict['title'] = title
    return dict


TITLE_OPTIONS = ['Mr', 'Miss', 'Ms', 'Mrs']