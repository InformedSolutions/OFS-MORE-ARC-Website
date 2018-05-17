from django.http import HttpResponseRedirect
from django.conf import settings
from django.urls import reverse
from django.views import View
from django.shortcuts import render
from django.utils.http import urlencode

from arc_application.forms.form_helper import initial_data_filler, data_saver
from ...forms.update_detail_forms.update_contact_details import UpdateEmail, UpdatePhoneNumber, UpdateAddPhoneNumber
from ...models import UserDetails, Application
from ...views import has_group


class ChangeDetails(View):
    form = None
    page_title = None
    pre_text = ''
    post_text = ''
    alt_text = ''

    def get(self, request):
        app_id = request.GET['id']
        context = {
            'application_id': app_id,
            'page_title': self.page_title,
            'pre_text': self.pre_text,
            'post_text': self.post_text,
            'submit_alt_text': self.alt_text,
            'form': self.form(id=UserDetails.objects.get(application_id=app_id)),
            'cc_user': has_group(request.user, settings.CONTACT_CENTRE)
        }
        return render(request, 'update_details/update_field.html', context)

    def post(self, request):
        app_id = request.POST['id']
        application = Application.objects.get(application_id=app_id)
        contact_record = UserDetails.objects.get(application_id=application)
        output_form = self.form(request.POST, contact_record.pk,
                                id=UserDetails.objects.get(application_id=request.GET['id']))
        
        context = {
            'application_id': app_id,
            'page_title': self.page_title,
            'pre_text': self.pre_text,
            'post_text': self.post_text,
            'submit_alt_text': self.alt_text,
            'form': output_form,
            'cc_user': has_group(request.user, settings.CONTACT_CENTRE)
        }

        initial_data_filler(output_form, UserDetails, contact_record.pk)
        if output_form.is_valid():
            data_saver(output_form, UserDetails, contact_record.pk)
            return HttpResponseRedirect(self.build_url('search_summary', get={'id': app_id}))
        else:
            return render(request, 'update_details/update_field.html', context)

    def build_url(self, *args, **kwargs):
        get = kwargs.pop('get', {})
        url = reverse(*args, **kwargs)
        if get:
            url += '?' + urlencode(get)
        return url


class UpdateEmailView(ChangeDetails):
    form = UpdateEmail
    page_title = "Update the applicant's email"


class UpdatePhoneNumberView(ChangeDetails):
    form = UpdatePhoneNumber
    page_title = "Update the applicant's mobile phone number"


class UpdateAddPhoneNumberView(ChangeDetails):
    form = UpdateAddPhoneNumber
    page_title = "Update the applicant's alternative phone number"


class UpdateSecurityQuestionView(ChangeDetails):
    pass


class UpdateSecurityAnswerView(ChangeDetails):
    pass
