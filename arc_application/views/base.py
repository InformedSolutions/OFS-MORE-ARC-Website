import json
from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserModel
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.generic import ListView
from django.utils.http import urlsafe_base64_decode
from django.utils.text import capfirst
from django.urls import reverse
from govuk_forms.forms import GOVUKForm
from timeline_logger.models import TimelineLog


from ..models import ApplicantName, ApplicantPersonalDetails, Application, Arc, ArcComments, \
    ApplicantHomeAddress, AdultInHome, CriminalRecordCheck, FirstAidTraining, Reference


@login_required()
def summary_page(request):
    """
    Arc Summary page to view assigned applications and manage them
    :param request: Http request, must be logged in with a user that has access
    :return: render static template
    """
    # Check if user has access and initiate error messages
    if has_group(request.user, settings.ARC_GROUP):

        error_exist = 'false'
        error_title = ''
        error_text = ''
        empty = 'false'
        assign_response = True

        # If the 'New Application' button has been clicked get new application
        if request.method == 'POST':
            assign_response = assign_new_application(request)
        entries = Arc.objects.filter(user_id=request.user.id)
        obj = []

        # For each application assigned to the user
        for entry in entries:
            # Get data to display in table
            response = get_table_data(entry)
            obj.append(response)
        # If no applications are assigned hide the table

        if len(obj) == 0:
            empty = 'true'

        # If you have reached the limit you will receive an error message
        if assign_response == 'LIMIT_REACHED':
            error_exist = 'true'
            error_title = 'You have reached the limit'
            error_text = 'You have already reached the maximum (' + str(settings.APPLICATION_LIMIT) + ') applications'

        # No applications available for review
        if not assign_response:
            error_exist = 'true'
            error_title = 'No Available Applications'
            error_text = 'There are currently no more applications ready for a review'

        variables = {
            'entries': obj,
            'empty': empty,
            'error_exist': error_exist,
            'error_title': error_title,
            'error_text': error_text
        }

        return render(request, './summary.html', variables)
    else:
        return HttpResponseRedirect(settings.URL_PREFIX + '/login/')


def get_table_data(obj):
    """
    Get data to display in summary table
    :param obj: Arc object
    :return: Dict that essentially extends Arc and includes a few more fields
    """

    local_application_id = obj.application_id

    if Application.objects.filter(pk=local_application_id).count() > 0:
        obj.application = Application.objects.get(application_id=local_application_id)
        arc_user = Arc.objects.get(application_id=local_application_id)
        obj.date_submitted = obj.application.date_submitted
        obj.last_accessed = arc_user.last_accessed
        obj.app_type = 'Childminder'

    if ApplicantPersonalDetails.objects.filter(application_id=local_application_id).count() > 0:
        personal_details = ApplicantPersonalDetails.objects.get(application_id=local_application_id)
        applicant_name = ApplicantName.objects.get(personal_detail_id=personal_details.personal_detail_id)
        obj.applicant_name = applicant_name.first_name + ' ' + applicant_name.last_name
    return obj


def assign_new_application(request):
    """
    Assign a new application and initiate ArcStatus row
    :param request: HTTP request
    :return: A Json with the Application Id, 'Limit Reached' if a user has too many already assigned, and False if none availible
    """
    if Arc.objects.filter(user_id=request.user.id).count() == settings.APPLICATION_LIMIT:
        return 'LIMIT_REACHED'

    app_id = get_oldest_application_id()

    if app_id is None:
        return False

    # TRIGGER
    # This is where all applications are assigned to the arc users
    # This is BDD scenario 2
    # According to the mockup it should say 'Assigned to USERNAME'

    if Application.objects.filter(pk=app_id).count() > 0:

        application = Application.objects.get(application_id=app_id)

        # Update app status to Arc review when assigned to an arc user
        application.application_status = 'ARC_REVIEW'
        application.save()

        if not Arc.objects.filter(pk=app_id).exists():

            arc_user = Arc.objects.create(application_id=app_id)
            arc_user.login_details_review = "NOT_STARTED"
            arc_user.childcare_type_review = "NOT_STARTED"
            arc_user.personal_details_review = "NOT_STARTED"
            arc_user.first_aid_review = "NOT_STARTED"
            arc_user.dbs_review = "NOT_STARTED"
            arc_user.health_review = "NOT_STARTED"
            arc_user.references_review = "NOT_STARTED"
            arc_user.people_in_home_review = "NOT_STARTED"
            arc_user.declaration_review = "NOT_STARTED"
            arc_user.app_type = 'Childminder'
            arc_user.last_accessed = str(application.date_updated.strftime('%d/%m/%Y'))
            arc_user.user_id = request.user.id
            arc_user.save()

        else:

            # If an Arc review has already started (but the application was released or resubmitted) then add user_id,
            # and update last_accessed

            arc_user = Arc.objects.get(pk=app_id)
            arc_user.last_accessed = str(application.date_updated.strftime('%d/%m/%Y'))
            arc_user.user_id = request.user.id
            arc_user.save()

        TimelineLog.objects.create(
            content_object=arc_user,
            user=request.user,
            template='timeline_logger/application_action.txt',
            extra_data={'user_type': 'reviewer', 'action': 'assigned', 'entity': 'application'}
        )

        return JsonResponse({'message': arc_user.application_id})


def get_assigned_apps(request):
    """
    Get applications currently supplied to the user
    :param request: HTTP Request
    :return: a list of Arc Review objects
    """
    apps = Arc.objects.all()
    arr = []
    for i in apps:
        arr.append(i)
    return arr


def get_oldest_application_id():
    """
    Get the oldest application (where payment is successful)
    :return: Application ID
    """
    application_list = Application.objects.exclude(date_submitted=None)
    for application in application_list:
        # Only return applications that have been submitted successfully by childminder (or released by arc)
        if application.application_status == 'SUBMITTED':
            return application.application_id


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
    return render(request, './registration/login.html', variables)


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


@login_required()
def release(request, application_id):
    """
    This is purely to handle the /release url on the arc summary page
    :param request: HTTP Request
    :param application_id: Childminder app id (PK)
    :return: release_application request
    """
    return release_application(request, application_id, 'SUBMITTED')

# TRIGGER
# This is where all applications are released (3 different messages)
# 1. If status == 'COMPLETED' it has been released by Arc User (not mentioned in BDD)
# 2. If status == 'FURTHER_INFORMATION' it needs to be returned to the applicant (BDD #3)
# 3. If status == 'ACCEPTED' it has been submitted to Cygnum (BDD #8)

def release_application(request, application_id, status):
    """
    Release application- essentiall remove the user_id field so that it's not assigned to anyone but the review status
    should remain

    :param request: HTTP Request
    :param application_id: Childminder app id (PK)
    :param status: what status to update the application with on release
    :return: Either redirect on success, or return error page (TBC)
    """

    # Logging
    """
    if ApplicantPersonalDetails.objects.filter(application_id=local_application_id).count() > 0:
                personal_details = ApplicantPersonalDetails.objects.get(
                    application_id=local_application_id
                )
                applicant_name = ApplicantName.objects.get(
                    personal_detail_id=personal_details.personal_detail_id
                )
                obj.applicant_name = applicant_name.first_name + ' ' + applicant_name.last_name
    """

    if Application.objects.filter(application_id=application_id).exists():
        app = Application.objects.get(application_id=application_id)
        app.application_status = status
        app.save()


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
    template_name = "auditlog_list.html"
    paginate_by = settings.TIMELINE_PAGINATE_BY

    def get_queryset(self, **kwargs):
        app_id = self.request.GET.get('id')
        queryset = TimelineLog.objects.filter(object_id=app_id).order_by('-timestamp')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AuditlogListView, self).get_context_data(**kwargs)

        if has_group(self.request.user, settings.CONTACT_CENTRE):
            context['back'] = reverse('search')

        if has_group(self.request.user, settings.ARC_GROUP):
            context['back'] =  reverse('task_list') + '?id=' + self.request.GET.get('id')

        return context


######################################################################################################
# Error Pages copied from Childminder

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
