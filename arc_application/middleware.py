"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- middleware.py --

@author: Informed Solutions
"""
from django.conf import settings


def globalise_url_prefix(request):
    """
    Middleware function to support Django applications being hosted on a
    URL prefixed path (e.g. for use with reverse proxies such as NGINX) rather
    than assuming application available on root index.
    """
    # return URL_PREFIX value defined in django settings.py for use by global view template
    return {'URL_PREFIX': settings.URL_PREFIX}


def globalise_server_name(request):
    """
    Middleware function to pass the server name to the footer
    :param request:
    :return: a dictionary containing the globalised server name
    """
    if hasattr(settings, 'SERVER_LABEL'):
        return {'SERVER_LABEL': settings.SERVER_LABEL}
    else:
        return {'SERVER_LABEL': None}


def set_tab_visibility(request):
    """
    Middleware function for determining tabs to show depending on the user Group
    :return: dict, (key, value) :
        (SHOW_REVIEW_TAB, True if user belongs to the ARC Group else False)
        (SHOW_UPLOAD_DBS_TAB, True if user belongs to the ARC Group else False)
    """
    is_arc_reviewer = request.user.groups.filter(name=settings.ARC_GROUP).exists()
    return {'SHOW_REVIEW_TAB': is_arc_reviewer, 'SHOW_DBS_UPLOAD_TAB': is_arc_reviewer}
