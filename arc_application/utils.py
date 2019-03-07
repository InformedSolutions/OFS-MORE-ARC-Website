from django.contrib.auth.models import Group


def has_group(user, group_name):
    """
    Check if user is in group
    :return: True if user is in group, else false
    """
    group = Group.objects.get(name=group_name)

    return True if group in user.groups.all() else False