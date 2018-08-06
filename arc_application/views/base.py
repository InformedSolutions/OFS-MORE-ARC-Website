from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserModel
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView
from django.utils.http import urlsafe_base64_decode
from django.utils.text import capfirst
from django.urls import reverse
from govuk_forms.forms import GOVUKForm
from timeline_logger.models import TimelineLog
from arc_application.review_util import reset_declaration

from arc_application.models import Application, Arc

from arc_application.services.db_gateways import NannyGatewayActions


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
    Release application- essentiall remove the user_id field so that it's not assigned to anyone but the review status
    should remain

    :param request: HTTP Request
    :param application_id: Childminder app id (PK)
    :param status: what status to update the application with on release
    :return: Either redirect on success, or return error page (TBC)
    """
    if Application.objects.filter(application_id=application_id).exists():
        app = Application.objects.get(application_id=application_id)
        app.application_status = status
        app.save()

        # reset declaration task
        if status == 'FURTHER_INFORMATION':
            reset_declaration(app)

    # If application_id doesn't correspond to a Childminder application, it must be a Nanny one.
    else:
        nanny_api_response = NannyGatewayActions().read('application', params={'application_id': application_id})
        record = nanny_api_response.record
        record['application_status'] = 'SUBMITTED'
        NannyGatewayActions().put('application', params=record)

    if Arc.objects.filter(application_id=application_id).exists():
        arc = Arc.objects.get(pk=application_id)
        arc.user_id = ''
        arc.save()

        log_action = {
            'COMPLETED': 'completed by',
            'FURTHER_INFORMATION': 'returned by',
            'ACCEPTED': 'accepted by',
            'SUBMITTED': 'released by',
            'ASSIGN': 'assigned to',
        }

        # trigger_audit_log(application_id, status, request.user)
        TimelineLog.objects.create(
            content_object=arc,
            user=request.user,
            template='timeline_logger/application_action.txt',
            extra_data={'user_type': 'reviewer', 'action': log_action[status], 'entity': 'application'}
        )

        return HttpResponseRedirect('/arc/summary')


class AuditlogListView(ListView):
    template_name = "childminder_templates/auditlog_list.html"
    paginate_by = settings.TIMELINE_PAGINATE_BY

    def get_queryset(self, **kwargs):
        app_id = self.request.GET.get('id')
        queryset = TimelineLog.objects.filter(object_id=app_id).order_by('-timestamp')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AuditlogListView, self).get_context_data(**kwargs)
        app_id = self.request.GET.get('id')
        context['application_reference'] = Application.objects.get(application_id=app_id).application_reference

        if has_group(self.request.user, settings.CONTACT_CENTRE):
            context['back'] = reverse('search')
            context['cc_user'] = True

        if has_group(self.request.user, settings.ARC_GROUP):
            context['arc_user'] = True
            context['back'] = reverse('task_list') + '?id=' + self.request.GET.get('id')

        return context


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
