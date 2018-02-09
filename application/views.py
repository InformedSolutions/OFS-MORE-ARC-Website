from django.contrib.auth import authenticate
from django.contrib.auth.forms import UsernameField, UserModel
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.utils.text import capfirst
from govuk_forms.forms import GOVUKForm
from django import forms
from django.contrib.auth import login as auth_login

from .models import Application, ArcReview


@login_required()
def summary_page(request):
    apps = get_assigned_apps(request)
    if request.method == 'POST':
        assign_new_application
    return render(request, './summary.html')


@login_required()
def assign_new_application(request):
    application_id = get_oldest_application_id()
    # ArcReview.objects.all().delete()
    arc_user = ArcReview.objects.create()
    arc_user.user_id = request.user.id
    arc_user.application_id = application_id
    arc_user.date_submitted = ArcReview.objects.filter(pk=application_id)
    arc_user.name = get_name(arc_user.application_id)
    arc_user.app_type = 'childminder'
    arc_user.save()
    return JsonResponse({'message': arc_user.application_id})


@login_required()
def delete_all(request):
    try:
        ArcReview.objects.all().delete()
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
    name = ''
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


def login(request):
    form = AuthenticationForm()
    variables = {
        'form': form
    }
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return HttpResponseRedirect('/summary')
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
