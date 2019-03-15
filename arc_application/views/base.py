import json

from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserModel
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.http import urlsafe_base64_decode
from django.utils.text import capfirst

from govuk_forms.forms import GOVUKForm
from timeline_logger.models import TimelineLog
from ..review_util import reset_declaration
from ..models import Application, Arc
from ..services.db_gateways import NannyGatewayActions


def custom_login(request):
    """
    Overridden django login method
    :param request: HTTP Request
    :return: Login
    """
    if has_group(request.user, settings.ARC_GROUP) and request.user.is_authenticated():
        return HttpResponseRedirect(settings.URL_PREFIX + '/summary')
    elif has_group(request.user, settings.CONTACT_CENTRE) and request.user.is_authenticated():
        return HttpResponseRedirect(settings.URL_PREFIX + '/search')

    if request.method == 'POST':

        form = AuthenticationForm(data=request.POST)
        variables = {
            'form': form
        }

        try:
            form.is_valid()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None and has_group(user, settings.ARC_GROUP) and not has_group(user,
                                                                                          settings.CONTACT_CENTRE):
                auth_login(request, user)
                return HttpResponseRedirect(settings.URL_PREFIX + '/summary')
            elif has_group(user, settings.CONTACT_CENTRE) and not has_group(user, settings.ARC_GROUP):
                auth_login(request, user)
                return HttpResponseRedirect(settings.URL_PREFIX + '/search')
            else:
                form.error_summary_title = 'There was a problem signing you in'

        except Exception as ex:
            print(ex)
            form.error_summary_title = 'There was a problem signing you in'
            form.get_invalid_login_error()
    else:
        form = AuthenticationForm()
    variables = {
        'form': form
    }
    return render(request, 'registration/login.html', variables)


def get_user(self, uidb64):
    try:
        # urlsafe_base64_decode() decodes to bytestring
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None
    return user


def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@login_required
def release(request, application_id):
    """
    This is purely to handle the /release url on the arc summary page
    :param request: HTTP Request
    :param application_id: Childminder app id (PK)
    :return: release_application request
    """
    return release_application(request, application_id, 'SUBMITTED')


@login_required
def release_application(request, application_id, status):
    """
    Release application, settings fields as appropriate for the specified new status.

    Essential to remove the user_id field so that it's not assigned to anyone but the review
    status should remain

    :param request: HTTP Request
    :param application_id: Childminder/Nanny/Etc application id (PK)
    :param status: what status to update the application with on release
    :return: Either redirect on success, or return error page (TBC)
    """
    if Application.objects.filter(application_id=application_id).exists():

        app = Application.objects.get(application_id=application_id)

        if status == 'FURTHER_INFORMATION':
            reset_declaration(app)
        elif status == 'ACCEPTED':
            app.date_accepted = datetime.now()

        app.application_status = status
        app.save()

        if status == 'ACCEPTED':
            # Import used here explicitly to prevent circular import
            from ..messaging import ApplicationExporter
            ApplicationExporter.export_childminder_application(application_id)

    # If application_id doesn't correspond to a Childminder application, it must be a Nanny one.
    else:
        nanny_api_response = NannyGatewayActions().read('application', params={'application_id': application_id})
        app = nanny_api_response.record

        if status == 'FURTHER_INFORMATION':
            app['declarations_status'] = 'NOT_STARTED'
        elif status == 'ACCEPTED':
            app['date_accepted'] = datetime.now()

        app['application_status'] = status
        NannyGatewayActions().put('application', params=app)

        if status == 'ACCEPTED':
            from ..messaging import ApplicationExporter
            application_reference = app['application_reference']
            ApplicationExporter.export_nanny_application(application_id, application_reference)

    # keep arc record but un-assign user from it
    if Arc.objects.filter(application_id=application_id).exists():
        arc = Arc.objects.get(pk=application_id)
        arc.user_id = ''
        arc.save()
        log_application_release(request, arc, app, status)
        return HttpResponseRedirect('/arc/summary')


def log_application_release(request, arc_object, app, status):
    log_action = {
        'COMPLETED': 'completed by',
        'FURTHER_INFORMATION': 'returned by',
        'ACCEPTED': 'accepted by',
        'SUBMITTED': 'released by',
        'ASSIGN': 'assigned to',
    }

    if isinstance(app, Application):  # If handling a Childminder application.
        TimelineLog.objects.create(
            content_object=arc_object,
            user=request.user,
            template='timeline_logger/application_action.txt',
            extra_data={'user_type': 'reviewer', 'action': log_action[status], 'entity': 'application'}
        )

    elif isinstance(app, dict):  # If handling a Nanny application.
        extra_data = {
                'user_type': 'reviewer',
                'action': log_action[status],
                'entity': 'application'
            }

        log_data = {
            'object_id': app['application_id'],
            'template': 'timeline_logger/application_action.txt',
            'user': request.user.username,
            'extra_data': json.dumps(extra_data)
        }

        NannyGatewayActions().create('timeline-log', params=log_data)


######################################################################################################
# Error Pages copied from Childminder

def error_403(request):
    """
    Method returning the 403 (Forbidden) error template
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 403 error template
    """
    data = {}
    return render(request, '403.html', data)


def error_404(request):
    """
    Method returning the 404 error template
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 404 error template
    """
    data = {}
    return render(request, '404.html', data)


def error_500(request):
    """
    Method returning the 500 error template
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 500 error template
    """
    data = {}
    return render(request, '500.html', data)


######################################################################################################
# Overwrited Django Authentication Methods


class AuthenticationForm(GOVUKForm):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        # Set the max length and label for the "username" field.
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        self.fields['username'].max_length = self.username_field.max_length or 254
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None or (
                    not has_group(self.user_cache, settings.ARC_GROUP) and not has_group(self.user_cache,
                                                                                         settings.CONTACT_CENTRE)) or (
                    has_group(self.user_cache, settings.ARC_GROUP) and has_group(self.user_cache,
                                                                                 settings.CONTACT_CENTRE)):
                raise forms.ValidationError(
                    'Username and password combination not recognised. Please try signing in again below')
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.
        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.
        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return forms.ValidationError('Please Enter a Valid Username and Password')
