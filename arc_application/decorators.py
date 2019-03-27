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
            url_app_id = request.GET.get("id", '')
            posted_app_id = request.POST.get("id", '')

            # if id specified in both places, ensure they are the same before performing auth check
            if url_app_id and posted_app_id and url_app_id != posted_app_id:
                raise PermissionDenied('GET and POST application IDs differ')

            # allow fall back to GET parameter if not in POST body
            application_id = posted_app_id or url_app_id

        arc_user_binding = Arc.objects.get(pk=application_id)

        # If an ARC binding is present but the user does not match the allocated user id, raise a 403
        if arc_user_binding is not None and (arc_user_binding.user_id != str(request.user.id)):
            raise PermissionDenied
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

