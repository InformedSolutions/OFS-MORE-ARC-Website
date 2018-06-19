"""
Custom decorators for authentication testing purposes
"""
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils import six
from .models import Arc


def group_required(group, login_url=None, raise_exception=False):
    """
    Decorator for views that checks whether a user has a group permission,
    redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """
    def check_perms(user):
        if isinstance(group, six.string_types):
            groups = (group,)
        else:
            groups = group

        if user.groups.filter(name__in=groups).exists():
            return True
        raise PermissionDenied
    return user_passes_test(check_perms, login_url=login_url)


def user_assigned_application(function):
    """
    Decorator to prevent ARC users accessing each other's applications (i.e. to which they are not assigned)
    :param function: callback to inner function (located below decorator)
    """
    def wrap(request, *args, **kwargs):
        if request.method == 'GET':
            application_id = request.GET["id"]
        else:
            application_id = request.POST["id"]

        arc_user_binding = Arc.objects.get(pk=application_id)

        # If an ARC binding is present but the user does not match the allocated user id, raise a 403
        if arc_user_binding is not None and (arc_user_binding.user_id != str(request.user.id)):
            raise PermissionDenied
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

