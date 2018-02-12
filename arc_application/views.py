import datetime
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UsernameField, UserModel
from django.contrib.auth.models import User, Group
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.utils.text import capfirst
from govuk_forms.forms import GOVUKForm
from django import forms
from django.contrib.auth import login as auth_login

from .models import Application, ArcReview, ApplicantPersonalDetails, ApplicantName


@login_required()
def summary_page(request):
    if has_group(request.user, 'arc'):
        entries = ArcReview.objects.filter(user_id=request.user.id).order_by('user_id')
        variables = {
            'entries': entries,
        }
        if request.method == 'POST':
            assign_new_application(request)
            entries = ArcReview.objects.filter(user_id=request.user.id).order_by('user_id')
            variables = {
                'entries': entries,
            }
            return render(request, './summary.html', variables)
        return render(request, './summary.html', variables)
    return JsonResponse({'message': 'Gotta login with correct access rights'})


def assign_new_application(request):
    if ArcReview.objects.filter(user_id=request.user.id).count() > 10:
        return JsonResponse({'message': 'Error you have already reached the maximum (10) applications'})
    else:
        local_application_id = get_oldest_application_id()
        if local_application_id == None:
            print("No Applications Availible")
    arc_user = ArcReview.objects.create()
    if Application.objects.filter(pk=local_application_id).count() > 0:
        application = Application.objects.get(application_id=local_application_id)
        arc_user.date_submitted = str(application.date_updated.strftime('%d/%m/%Y'))
        arc_user.user_id = request.user.id
        arc_user.application_id = local_application_id
        arc_user.app_type = 'Childminder'
        arc_user.last_accessed = str(datetime.datetime.now().strftime('%d/%m/%Y'))
        application = Application.objects.filter(pk=local_application_id)
        try:
            if ApplicantPersonalDetails.objects.filter(application_id=local_application_id).count() > 0:
                personal_details = ApplicantPersonalDetails.objects.get(application_id=local_application_id)
                applicant_name = ApplicantName.objects.get(personal_detail_id=personal_details.personal_detail_id)
                arc_user.applicant_name = applicant_name.first_name +' ' + applicant_name.last_name
        except Exception as ex:
            print(ex)
            arc_user.name = 'TEMP'
        arc_user.save()
    return JsonResponse({'message': arc_user.application_id})


@login_required()
def delete_all(request):
    try:
        ArcReview.objects.all().delete()
        JsonResponse({'message':'ArcReview Table deleted'})
    except Exception as ex:
        HttpResponse(ex)


def get_assigned_apps(request):
    apps = ArcReview.objects.all()
    arr = []
    for i in apps:
        arr.append(i)
    return arr


def get_name(application_id):
    # lookup app id, traverse throught tables and return name
    name = 'placeholder'
    return name


def get_oldest_application_id():
    application_list = Application.objects.all().order_by('date_created')
    for i in application_list:
        if len(ArcReview.objects.filter(pk=i.application_id)) == 0:
            return i.application_id
    # if it gets to here return error, no application for review


def get_users():
    users = User.objects.all()
    return users


def custom_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(settings.URL_PREFIX + '/summary')
    form = AuthenticationForm()
    variables = {
        'form': form
    }
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and has_group(user, 'arc'):
                auth_login(request, user)
                return HttpResponseRedirect(settings.URL_PREFIX + '/summary')
            else:
                return HttpResponse("Not signed in")
        except Exception as ex:
            print(ex)

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

def release_application(request, application_id):
    if len(ArcReview.objects.filter(application_id=application_id))==1:
        row = ArcReview.objects.get(application_id=application_id)
        row.delete()
        return HttpResponseRedirect('/arc/summary')
    else:
        return JsonResponse({"message": "fail"})#


def review_application(request, application_id):
    if len(ArcReview.objects.filter(application_id=application_id))==1:
        row = ArcReview.objects.get(application_id=application_id)

    else:
        return JsonResponse({"message": "fail"})
######################################################################################################

# Overwrited Django Auth Form
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
            if self.user_cache is None:
                raise self.get_invalid_login_error()
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
        return forms.ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
            params={'username': self.username_field.verbose_name},
        )
