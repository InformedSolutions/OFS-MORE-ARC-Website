"""
OFS-MORE-CCN3: ARC Review Service
-- update_contact_details.py --

@author: Informed Solutions
"""
import re

from govuk_forms.forms import GOVUKForm
from django import forms
from ...models import UserDetails, Application
from ..form_helper import initial_data_filler


class UpdateEmail(GOVUKForm):
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    error_summary_template_name = 'error-summary.html'

    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.this_user = kwargs.pop('id')
        login_id = self.this_user.login_id
        super(UpdateEmail, self).__init__(*args, **kwargs)
        initial_data_filler(self, UserDetails, login_id)

    def clean_email(self):
        """
        Email address validation
        :return: string
        """
        email = self.cleaned_data['email']
        # RegEx for valid e-mail addresses
        if re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", email) is None:
            raise forms.ValidationError('Please enter a valid email address')
        if len(email) == 0:
            raise forms.ValidationError('Please enter an email address')
        return email


class UpdatePhoneNumber(GOVUKForm):
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    error_summary_template_name = 'error-summary.html'

    mobile_number = forms.CharField(label='Mobile phone number')

    def __init__(self, *args, **kwargs):
        self.this_user = kwargs.pop('id')
        login_id = self.this_user.login_id
        super(UpdatePhoneNumber, self).__init__(*args, **kwargs)
        initial_data_filler(self, UserDetails, login_id)

    def clean_mobile_number(self):
        """
        Mobile number validation
        :return: string
        """
        mobile_number = self.cleaned_data['mobile_number']
        no_space_mobile_number = mobile_number.replace(' ', '')
        if re.match("^(07\d{8,12}|447\d{7,11})$", no_space_mobile_number) is None:
            raise forms.ValidationError('TBC')
        if len(no_space_mobile_number) > 11:
            raise forms.ValidationError('TBC')
        return mobile_number

class UpdateAddPhoneNumber(GOVUKForm):
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    error_summary_template_name = 'error-summary.html'

    add_phone_number = forms.CharField(label='Additional phone number')

    def __init__(self, *args, **kwargs):
        self.this_user = kwargs.pop('id')
        login_id = self.this_user.login_id
        super(UpdateAddPhoneNumber, self).__init__(*args, **kwargs)
        initial_data_filler(self, UserDetails, login_id)

    def clean_add_phone_number(self):
        """
        Phone number validation
        :return: string
        """
        add_phone_number = self.cleaned_data['add_phone_number']
        no_space_add_phone_number = add_phone_number.replace(' ', '')
        if add_phone_number != '':
            if re.match("^(0\d{8,12}|447\d{7,11})$", no_space_add_phone_number) is None:
                raise forms.ValidationError('TBC')
            if len(no_space_add_phone_number) > 11:
                raise forms.ValidationError('TBC')
        return add_phone_number


class UpdateSecurtiyQuestion(GOVUKForm):
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
