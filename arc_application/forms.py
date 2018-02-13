"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- forms.py --

@author: Informed Solutions
"""

import re

from datetime import date
from django import forms
from django.conf import settings
from govuk_forms.fields import SplitDateField
from govuk_forms.forms import GOVUKForm
from govuk_forms.widgets import CheckboxSelectMultiple, InlineRadioSelect, RadioSelect
from govuk_forms.fields import SplitDateField

from .customfields import TimeKnownField, ExpirySplitDateWidget, SelectDateWidget, ExpirySplitDateField
from .models import (AdultInHome,
                     ApplicantHomeAddress,
                     ApplicantName,
                     ApplicantPersonalDetails,
                     Application,
                     ChildcareType,
                     ChildInHome,
                     CriminalRecordCheck,
                     EYFS,
                     FirstAidTraining,
                     HealthDeclarationBooklet,
                     Reference,
                     UserDetails)


class AccountForm(GOVUKForm):
    """
    GOV.UK form for the Account selection page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class ContactEmailForm(GOVUKForm):
    """
    GOV.UK form for the Your login and contact details: email page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    email_address = forms.EmailField()

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your login and contact details: email form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ContactEmailForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            this_user = Application.objects.get(pk=self.application_id_local)
            login_id = this_user.login_id.login_id
            if UserDetails.objects.get(login_id=login_id).login_id != '':
                self.fields['email_address'].initial = UserDetails.objects.get(login_id=login_id).email

    def clean_email_address(self):
        """
        Email address validation
        :return: string
        """
        email_address = self.cleaned_data['email_address']
        # RegEx for valid e-mail addresses
        if re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", email_address) is None:
            raise forms.ValidationError('TBC')
        if len(email_address) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return email_address


class ContactPhoneForm(GOVUKForm):
    """
    GOV.UK form for the Your login and contact details: phone page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    mobile_number = forms.CharField(label='Mobile phone number')
    add_phone_number = forms.CharField(label='Additional phone number (optional)', required=False)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your login and contact details: phone form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ContactPhoneForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            this_user = Application.objects.get(pk=self.application_id_local)
            login_id = this_user.login_id.login_id
            self.fields['mobile_number'].initial = UserDetails.objects.get(login_id=login_id).mobile_number
            self.fields['add_phone_number'].initial = UserDetails.objects.get(login_id=login_id).add_phone_number

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


class QuestionForm(GOVUKForm):
    """
    GOV.UK form for the Your login and contact details: knowledge based question page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    security_question = forms.CharField(label='Knowledge based question', required=True)
    security_answer = forms.CharField(label='Knowledge based answer', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your login and contact details: knowledge based question form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(QuestionForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            this_user = Application.objects.get(pk=self.application_id_local)
            login_id = this_user.login_id.login_id
            self.fields['security_question'].initial = UserDetails.objects.get(login_id=login_id).security_question
            self.fields['security_answer'].initial = UserDetails.objects.get(login_id=login_id).security_answer

    def clean_security_question(self):
        security_question = self.cleaned_data['security_question']
        if len(security_question) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return security_question

    def clean_security_answer(self):
        security_answer = self.cleaned_data['security_answer']
        if len(security_answer) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return security_answer


class ContactSummaryForm(GOVUKForm):
    """
    GOV.UK form for the Your login and contact details: summary page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class TypeOfChildcareGuidanceForm(GOVUKForm):
    """
    GOV.UK form for the Type of childcare: guidance page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class TypeOfChildcareAgeGroupsForm(GOVUKForm):
    """
    GOV.UK form for the Type of childcare task
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    CHILDCARE_AGE_CHOICES = (
        ('0-5', '0 to 5 year olds'),
        ('5-8', '5 to 7 year olds'),
        ('8over', '8 years or older'),
    )
    type_of_childcare = forms.MultipleChoiceField(
        required=True,
        widget=CheckboxSelectMultiple,
        choices=CHILDCARE_AGE_CHOICES,
        label='What age groups will you be caring for?',
        help_text='Tick all that apply'
    )

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Type of childcare form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(TypeOfChildcareAgeGroupsForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if ChildcareType.objects.filter(application_id=self.application_id_local).count() > 0:
            childcare_record = ChildcareType.objects.get(application_id=self.application_id_local)
            zero_to_five_status = childcare_record.zero_to_five
            five_to_eight_status = childcare_record.five_to_eight
            eight_plus_status = childcare_record.eight_plus
            if (zero_to_five_status is True) & (five_to_eight_status is True) & (eight_plus_status is True):
                self.fields['type_of_childcare'].initial = ['0-5', '5-8', '8over']
            elif (zero_to_five_status is True) & (five_to_eight_status is True) & (eight_plus_status is False):
                self.fields['type_of_childcare'].initial = ['0-5', '5-8']
            elif (zero_to_five_status is True) & (five_to_eight_status is False) & (eight_plus_status is True):
                self.fields['type_of_childcare'].initial = ['0-5', '8over']
            elif (zero_to_five_status is False) & (five_to_eight_status is True) & (eight_plus_status is True):
                self.fields['type_of_childcare'].initial = ['5-8', '8over']
            elif (zero_to_five_status is True) & (five_to_eight_status is False) & (eight_plus_status is False):
                self.fields['type_of_childcare'].initial = ['0-5']
            elif (zero_to_five_status is False) & (five_to_eight_status is True) & (eight_plus_status is False):
                self.fields['type_of_childcare'].initial = ['5-8']
            elif (zero_to_five_status is False) & (five_to_eight_status is False) & (eight_plus_status is True):
                self.fields['type_of_childcare'].initial = ['8over']
            elif (zero_to_five_status is False) & (five_to_eight_status is False) & (eight_plus_status is False):
                self.fields['type_of_childcare'].initial = []
        self.fields['type_of_childcare'].error_messages = {
            'required': 'You must select at least one age group to continue with your application'}


class TypeOfChildcareRegisterForm(GOVUKForm):
    """
    GOV.UK form for the Type of childcare: register page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class EmailLoginForm(GOVUKForm):
    """
    GOV.UK form for the page to log back into an application
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    email_address = forms.EmailField()

    def clean_email_address(self):
        """
        Email address validation
        :return: string
        """
        email_address = self.cleaned_data['email_address']
        if re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", email_address) is None:
            raise forms.ValidationError('Please enter a valid e-mail address.')
        return email_address


class VerifyPhoneForm(GOVUKForm):
    """
    GOV.UK form for the page to verify an SMS code
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    magic_link_sms = forms.CharField(label='Security code', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the SMS code verification form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.magic_link_email = kwargs.pop('id')
        super(VerifyPhoneForm, self).__init__(*args, **kwargs)

    def clean_magic_link_sms(self):
        """
        SMS code validation
        :return: string
        """
        magic_link_sms = self.cleaned_data['magic_link_sms']
        if (UserDetails.objects.filter(magic_link_sms=magic_link_sms, magic_link_email=self.magic_link_email).count()
                == 0):
            raise forms.ValidationError('TBC')
        return magic_link_sms


class VerifySecurityQuestionForm(GOVUKForm):
    """
    GOV.UK form for the page to verify an SMS code
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    security_answer = forms.CharField(label='Security question', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the SMS code verification form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(VerifySecurityQuestionForm, self).__init__(*args, **kwargs)

    def clean_security_answer(self):
        security_answer = self.cleaned_data['security_answer']
        if UserDetails.objects.filter(security_answer=security_answer).count() == 0:
            raise forms.ValidationError('TBC')
        return security_answer


class PersonalDetailsGuidanceForm(GOVUKForm):
    """
    GOV.UK form for the Your personal details: guidance page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class PersonalDetailsNameForm(GOVUKForm):
    """
    GOV.UK form for the Your personal details: name page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    first_name = forms.CharField(label='First name')
    middle_names = forms.CharField(label='Middle names (if you have any)', required=False)
    last_name = forms.CharField(label='Last name')

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: name form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsNameForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if ApplicantPersonalDetails.objects.filter(application_id=self.application_id_local).count() > 0:
            personal_detail_id = ApplicantPersonalDetails.objects.get(
                application_id=self.application_id_local).personal_detail_id
            applicant_name_record = ApplicantName.objects.get(personal_detail_id=personal_detail_id)
            self.fields['first_name'].initial = applicant_name_record.first_name
            self.fields['middle_names'].initial = applicant_name_record.middle_names
            self.fields['last_name'].initial = applicant_name_record.last_name

    def clean_first_name(self):
        """
        First name validation
        :return: string
        """
        first_name = self.cleaned_data['first_name']
        if re.match("^[A-zÀ-ÿ- ]+$", first_name) is None:
            raise forms.ValidationError('TBC')
        if len(first_name) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return first_name

    def clean_middle_names(self):
        """
        Middle names validation
        :return: string
        """
        middle_names = self.cleaned_data['middle_names']
        if middle_names != '':
            if re.match("^[A-zÀ-ÿ- ]+$", middle_names) is None:
                raise forms.ValidationError('TBC')
            if len(middle_names) > 100:
                raise forms.ValidationError('Please enter 100 characters or less.')
        return middle_names

    def clean_last_name(self):
        """
        Last name validation
        :return: string
        """
        last_name = self.cleaned_data['last_name']
        if re.match("^[A-zÀ-ÿ- ]+$", last_name) is None:
            raise forms.ValidationError('TBC')
        if len(last_name) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return last_name


class PersonalDetailsDOBForm(GOVUKForm):
    """
    GOV.UK form for the Your personal details: date of birth page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    date_of_birth = SplitDateField(label='Date of birth', help_text='For example, 31 03 1980')

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: date of birth form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsDOBForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form        
        if ApplicantPersonalDetails.objects.filter(application_id=self.application_id_local).count() > 0:
            personal_details_record = ApplicantPersonalDetails.objects.get(application_id=self.application_id_local)
            self.fields['date_of_birth'].initial = [personal_details_record.birth_day,
                                                    personal_details_record.birth_month,
                                                    personal_details_record.birth_year]

    def clean_date_of_birth(self):
        """
        Date of birth validation (calculate if age is less than 18)
        :return: string
        """
        birth_day = self.cleaned_data['date_of_birth'].day
        birth_month = self.cleaned_data['date_of_birth'].month
        birth_year = self.cleaned_data['date_of_birth'].year
        applicant_dob = date(birth_year, birth_month, birth_day)
        today = date.today()
        age = today.year - applicant_dob.year - ((today.month, today.day) < (applicant_dob.month, applicant_dob.day))
        if age < 18:
            raise forms.ValidationError('You have to be 18 to childmind.')
        return birth_day, birth_month, birth_year


class PersonalDetailsHomeAddressForm(GOVUKForm):
    """
    GOV.UK form for the Your personal details: home address page for postcode search
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    postcode = forms.CharField(label='Postcode')

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: home address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsHomeAddressForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id, current_address=True).count() > 0:
            self.fields['postcode'].initial = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                               current_address=True).postcode

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        if re.match("^[A-Za-z0-9 ]{5,8}$", postcode) is None:
            raise forms.ValidationError('TBC.')
        return postcode


class PersonalDetailsHomeAddressManualForm(GOVUKForm):
    """
    GOV.UK form for the Your personal details: home address page for manual entry
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    street_name_and_number = forms.CharField(label='Address line 1')
    street_name_and_number2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(label='Town or city')
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(label='Postcode')

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: home address form for manual entry
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsHomeAddressManualForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id,
                                               current_address=True).count() > 0:
            applicant_home_address = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                      current_address=True)
            self.fields['street_name_and_number'].initial = applicant_home_address.street_line1
            self.fields['street_name_and_number2'].initial = applicant_home_address.street_line2
            self.fields['town'].initial = applicant_home_address.town
            self.fields['county'].initial = applicant_home_address.county
            self.fields['postcode'].initial = applicant_home_address.postcode

    def clean_street_name_and_number(self):
        """
        Street name and number validation
        :return: string
        """
        street_name_and_number = self.cleaned_data['street_name_and_number']
        if len(street_name_and_number) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return street_name_and_number

    def clean_street_name_and_number2(self):
        """
        Street name and number line 2 validation
        :return: string
        """
        street_name_and_number2 = self.cleaned_data['street_name_and_number2']
        if len(street_name_and_number2) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return street_name_and_number2

    def clean_town(self):
        """
        Town validation
        :return: string
        """
        town = self.cleaned_data['town']
        if re.match("^[A-Za-z- ]+$", town) is None:
            raise forms.ValidationError('TBC.')
        if len(town) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return town

    def clean_county(self):
        """
        County validation
        :return: string
        """
        county = self.cleaned_data['county']
        if county != '':
            if re.match("^[A-Za-z- ]+$", county) is None:
                raise forms.ValidationError('TBC.')
            if len(county) > 100:
                raise forms.ValidationError('Please enter 100 characters or less.')
        return county

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        if re.match("^[A-Za-z0-9 ]{5,8}$", postcode) is None:
            raise forms.ValidationError('TBC.')
        return postcode


class PersonalDetailsHomeAddressLookupForm(GOVUKForm):
    """
    GOV.UK form for the Your personal details: home address page for postcode search results
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    address = forms.ChoiceField(label='Select address', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: home address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.choices = kwargs.pop('choices')
        super(PersonalDetailsHomeAddressLookupForm, self).__init__(*args, **kwargs)
        self.fields['address'].choices = self.choices


class PersonalDetailsLocationOfCareForm(GOVUKForm):
    """
    GOV.UK form for the Your personal details: location of care page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    location_of_care = forms.ChoiceField(label='Is this where you will be looking after the children?', choices=options,
                                         widget=InlineRadioSelect, required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: location of care form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsLocationOfCareForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id, current_address=True).count() > 0:
            self.fields['location_of_care'].initial = ApplicantHomeAddress.objects.get(
                personal_detail_id=personal_detail_id, current_address=True).childcare_address


class PersonalDetailsChildcareAddressForm(GOVUKForm):
    """
    GOV.UK form for the Your personal details: childcare address page for postcode search
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    postcode = forms.CharField(label='Postcode')

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: childcare address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsChildcareAddressForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id,
                                               childcare_address='True').count() > 0:
            self.fields['postcode'].initial = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                               childcare_address='True').postcode

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        if re.match("^[A-Za-z0-9 ]{5,8}$", postcode) is None:
            raise forms.ValidationError('TBC.')
        return postcode


class PersonalDetailsChildcareAddressManualForm(GOVUKForm):
    """
    GOV.UK form for the Your personal details: childcare address page for manual entry
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    street_name_and_number = forms.CharField(label='Address line 1')
    street_name_and_number2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(label='Town or city')
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(label='Postcode')

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: childcare address form for manual entry
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsChildcareAddressManualForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id,
                                               childcare_address='True').count() > 0:
            childcare_address = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                 childcare_address='True')
            self.fields['street_name_and_number'].initial = childcare_address.street_line1
            self.fields['street_name_and_number2'].initial = childcare_address.street_line2
            self.fields['town'].initial = childcare_address.town
            self.fields['county'].initial = childcare_address.county
            self.fields['postcode'].initial = childcare_address.postcode

    def clean_street_name_and_number(self):
        """
        Street name and number validation
        :return: string
        """
        street_name_and_number = self.cleaned_data['street_name_and_number']
        if len(street_name_and_number) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return street_name_and_number

    def clean_street_name_and_number2(self):
        """
        Street name and number line 2 validation
        :return: string
        """
        street_name_and_number2 = self.cleaned_data['street_name_and_number2']
        if len(street_name_and_number2) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return street_name_and_number2

    def clean_town(self):
        """
        Town validation
        :return: string
        """
        town = self.cleaned_data['town']
        if re.match("^[A-Za-z- ]+$", town) is None:
            raise forms.ValidationError('TBC')
        if len(town) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return town

    def clean_county(self):
        """
        County validation
        :return: string
        """
        county = self.cleaned_data['county']
        if county != '':
            if re.match("^[A-Za-z- ]+$", county) is None:
                raise forms.ValidationError('TBC')
            if len(county) > 100:
                raise forms.ValidationError('Please enter 100 characters or less.')
        return county

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        if re.match("^[A-Za-z0-9 ]{5,8}$", postcode) is None:
            raise forms.ValidationError('TBC')
        return postcode


class PersonalDetailsChildcareAddressLookupForm(GOVUKForm):
    """
    GOV.UK form for the Your personal details: childcare address page for postcode search results
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    address = forms.ChoiceField(label='Select address', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: childcare address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.choices = kwargs.pop('choices')
        super(PersonalDetailsChildcareAddressLookupForm, self).__init__(*args, **kwargs)
        self.fields['address'].choices = self.choices


class PersonalDetailsSummaryForm(GOVUKForm):
    """
    GOV.UK form for the Your personal details: summary page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class FirstAidTrainingGuidanceForm(GOVUKForm):
    """
    GOV.UK form for the First aid training: guidance page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class FirstAidTrainingDetailsForm(GOVUKForm):
    """
    GOV.UK form for the First aid training: details page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    first_aid_training_organisation = forms.CharField(label='First aid training organisation')
    title_of_training_course = forms.CharField(label='Title of training course')
    course_date = SplitDateField(label='Course date', help_text='For example, 31 03 2016')

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the First aid training: details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(FirstAidTrainingDetailsForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form        
        if FirstAidTraining.objects.filter(application_id=self.application_id_local).count() > 0:
            first_aid_record = FirstAidTraining.objects.get(application_id=self.application_id_local)
            self.fields['first_aid_training_organisation'].initial = first_aid_record.training_organisation
            self.fields['title_of_training_course'].initial = first_aid_record.course_title
            self.fields['course_date'].initial = [first_aid_record.course_day,
                                                  first_aid_record.course_month,
                                                  first_aid_record.course_year]


class FirstAidTrainingDeclarationForm(GOVUKForm):
    """
    GOV.UK form for the First aid training: declaration page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    declaration = forms.BooleanField(label='I will show my first aid certificate to the inspector', required=True)


class FirstAidTrainingRenewForm(GOVUKForm):
    """
    GOV.UK form for the First aid training: renew page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    renew_a = forms.BooleanField(label='I will renew my first aid training in the next few months', required=True)
    renew_b = forms.BooleanField(label='I will show my first aid certificate to the inspector', required=True)


class FirstAidTrainingTrainingForm(GOVUKForm):
    """
    GOV.UK form for the First aid training: training page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class FirstAidTrainingSummaryForm(GOVUKForm):
    """
    GOV.UK form for the First aid training: summary page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class EYFSGuidanceForm(GOVUKForm):
    """
    GOV.UK form for the Early Years knowledge: guidance page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class EYFSKnowledgeForm(GOVUKForm):
    """
    GOV.UK form for the Early Years knowledge: knowledge page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    eyfs_understand = forms.ChoiceField(label='Do you understand the Early Years Foundation Stage?', choices=options,
                                        widget=InlineRadioSelect, required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Early Years knowledge: knowledge form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(EYFSKnowledgeForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if EYFS.objects.filter(application_id=self.application_id_local).count() > 0:
            eyfs_record = EYFS.objects.get(application_id=self.application_id_local)
            self.fields['eyfs_understand'].initial = eyfs_record.eyfs_understand


class EYFSTrainingForm(GOVUKForm):
    """
    GOV.UK form for the EYFS: training page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    eyfs_training_declare = forms.BooleanField(label='I will go on an early years training course', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Early Years knowledge: training form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(EYFSTrainingForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if EYFS.objects.filter(application_id=self.application_id_local).count() > 0:
            eyfs_record = EYFS.objects.get(application_id=self.application_id_local)
            self.fields['eyfs_training_declare'].initial = eyfs_record.eyfs_training_declare


class EYFSQuestionsForm(GOVUKForm):
    """
    GOV.UK form for the EYFS: training page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    eyfs_questions_declare = forms.BooleanField(label='I am happy to answer questions about my early years knowledge',
                                                required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Early Years knowledge: questions form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(EYFSQuestionsForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if EYFS.objects.filter(application_id=self.application_id_local).count() > 0:
            eyfs_record = EYFS.objects.get(application_id=self.application_id_local)
            self.fields['eyfs_questions_declare'].initial = eyfs_record.eyfs_questions_declare


class EYFSSummaryForm(GOVUKForm):
    """
    GOV.UK form for the Early Years knowledge: summary page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class DBSCheckGuidanceForm(GOVUKForm):
    """
    GOV.UK form for the Your criminal record (DBS) check: guidance page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class DBSCheckDBSDetailsForm(GOVUKForm):
    """
    GOV.UK form for the Your criminal record (DBS) check: details page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    dbs_certificate_number = forms.IntegerField(label='DBS certificate number',
                                                help_text='12-digit number on your certificate',
                                                required=True)
    convictions = forms.ChoiceField(label='Do you have any cautions or convictions?',
                                    help_text='Include any information recorded on your certificate',
                                    choices=options, widget=InlineRadioSelect,
                                    required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your criminal record (DBS) check: details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(DBSCheckDBSDetailsForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form 
        if CriminalRecordCheck.objects.filter(application_id=self.application_id_local).count() > 0:
            dbs_record = CriminalRecordCheck.objects.get(application_id=self.application_id_local)
            self.fields['dbs_certificate_number'].initial = dbs_record.dbs_certificate_number
            self.fields['convictions'].initial = dbs_record.cautions_convictions

    def clean_dbs_certificate_number(self):
        """
        DBS certificate number validation
        :return: integer
        """
        dbs_certificate_number = self.cleaned_data['dbs_certificate_number']
        if len(str(dbs_certificate_number)) > 12:
            raise forms.ValidationError('TBC')
        if len(str(dbs_certificate_number)) < 12:
            raise forms.ValidationError('TBC')
        return dbs_certificate_number


class DBSCheckUploadDBSForm(GOVUKForm):
    """
    GOV.UK form for the Your criminal record (DBS) check: upload DBS page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    declaration = forms.BooleanField(label='I will send my original DBS certificate to Ofsted', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your criminal record (DBS) check: upload DBS form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(DBSCheckUploadDBSForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if CriminalRecordCheck.objects.filter(application_id=self.application_id_local).count() > 0:
            dbs_record_declare = CriminalRecordCheck.objects.get(
                application_id=self.application_id_local).send_certificate_declare
            if dbs_record_declare is True:
                self.fields['declaration'].initial = '1'
            elif dbs_record_declare is False:
                self.fields['declaration'].initial = '0'


class DBSCheckSummaryForm(GOVUKForm):
    """
    GOV.UK form for the Your criminal record (DBS) check: summary page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class HealthIntroForm(GOVUKForm):
    """
    GOV.UK form for the Your health: intro page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class HealthBookletForm(GOVUKForm):
    """
    GOV.UK form for the Your health: intro page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    send_hdb_declare = forms.BooleanField(label='I will send the completed booklet to Ofsted', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your health: booklet form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(HealthBookletForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if HealthDeclarationBooklet.objects.filter(application_id=self.application_id_local).count() > 0:
            hdb_declare = HealthDeclarationBooklet.objects.get(
                application_id=self.application_id_local).send_hdb_declare
            if hdb_declare is True:
                self.fields['send_hdb_declare'].initial = '1'
            elif hdb_declare is False:
                self.fields['send_hdb_declare'].initial = '0'


class ReferenceIntroForm(GOVUKForm):
    """
    GOV.UK form for the 2 references: intro page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class FirstReferenceForm(GOVUKForm):
    """
    GOV.UK form for the 2 references: first reference page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    first_name = forms.CharField(label='First name', required=True)
    last_name = forms.CharField(label='Last name', required=True)
    relationship = forms.CharField(label='How do they know you?', help_text='For instance, friend or neighbour',
                                   required=True)
    time_known = TimeKnownField(label='How long have they known you?', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: first reference form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(FirstReferenceForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form        
        if Reference.objects.filter(application_id=self.application_id_local, reference=1).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local, reference=1)
            self.fields['first_name'].initial = reference_record.first_name
            self.fields['last_name'].initial = reference_record.last_name
            self.fields['relationship'].initial = reference_record.relationship
            self.fields['time_known'].initial = [reference_record.years_known, reference_record.months_known]

    def clean_first_name(self):
        """
        First name validation
        :return: string
        """
        first_name = self.cleaned_data['first_name']
        if re.match("^[A-zÀ-ÿ- ]+$", first_name) is None:
            raise forms.ValidationError('TBC')
        if len(first_name) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return first_name

    def clean_last_name(self):
        """
        Last name validation
        :return: string
        """
        last_name = self.cleaned_data['last_name']
        if re.match("^[A-zÀ-ÿ- ]+$", last_name) is None:
            raise forms.ValidationError('TBC')
        if len(last_name) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return last_name

    def clean_time_known(self):
        """
        Time known validation: reference must be known for 1 year or more
        :return: integer, integer
        """
        years_known = self.cleaned_data['time_known'][1]
        months_known = self.cleaned_data['time_known'][0]
        if months_known != 0:
            reference_known_time = years_known + (months_known / 12)
        elif months_known == 0:
            reference_known_time = years_known
        if reference_known_time < 1:
            raise forms.ValidationError('TBC.')
        return years_known, months_known


class ReferenceFirstReferenceAddressForm(GOVUKForm):
    """
    GOV.UK form for the 2 references: first reference address page for postcode search
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    postcode = forms.CharField(label='Postcode')

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: first reference address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceFirstReferenceAddressForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=1).count() > 0:
            self.fields['postcode'].initial = Reference.objects.get(application_id=self.application_id_local,
                                                                    reference=1).postcode

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        if re.match("^[A-Za-z0-9 ]{5,8}$", postcode) is None:
            raise forms.ValidationError('TBC.')
        return postcode


class ReferenceFirstReferenceAddressManualForm(GOVUKForm):
    """
    GOV.UK form for the 2 references: first reference address page for manual entry
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    street_name_and_number = forms.CharField(label='Address line 1')
    street_name_and_number2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(label='Town or city')
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(label='Postcode')
    country = forms.CharField(label='Country', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: first reference address form for manual entry
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceFirstReferenceAddressManualForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=1).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local, reference=1)
            self.fields['street_name_and_number'].initial = reference_record.street_line1
            self.fields['street_name_and_number2'].initial = reference_record.street_line2
            self.fields['town'].initial = reference_record.town
            self.fields['county'].initial = reference_record.county
            self.fields['postcode'].initial = reference_record.postcode
            self.fields['country'].initial = reference_record.country

    def clean_street_name_and_number(self):
        """
        Street name and number validation
        :return: string
        """
        street_name_and_number = self.cleaned_data['street_name_and_number']
        if len(street_name_and_number) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return street_name_and_number

    def clean_street_name_and_number2(self):
        """
        Street name and number line 2 validation
        :return: string
        """
        street_name_and_number2 = self.cleaned_data['street_name_and_number2']
        if len(street_name_and_number2) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return street_name_and_number2

    def clean_town(self):
        """
        Town validation
        :return: string
        """
        town = self.cleaned_data['town']
        if re.match("^[A-Za-z- ]+$", town) is None:
            raise forms.ValidationError('TBC')
        if len(town) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return town

    def clean_county(self):
        """
        County validation
        :return: string
        """
        county = self.cleaned_data['county']
        if county != '':
            if re.match("^[A-Za-z- ]+$", county) is None:
                raise forms.ValidationError('TBC')
            if len(county) > 100:
                raise forms.ValidationError('Please enter 100 characters or less.')
        return county

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        if re.match("^[A-Za-z0-9 ]{5,8}$", postcode) is None:
            raise forms.ValidationError('TBC')
        return postcode

    def clean_country(self):
        """
        Country validation
        :return: string
        """
        country = self.cleaned_data['country']
        if country != '':
            if re.match("^[A-Za-z- ]+$", country) is None:
                raise forms.ValidationError('TBC')
            if len(country) > 100:
                raise forms.ValidationError('Please enter 100 characters or less.')
        return country


class ReferenceFirstReferenceAddressLookupForm(GOVUKForm):
    """
    GOV.UK form for the 2 references: first reference address page for postcode search results
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    address = forms.ChoiceField(label='Select address', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: first reference address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.choices = kwargs.pop('choices')
        super(ReferenceFirstReferenceAddressLookupForm, self).__init__(*args, **kwargs)
        self.fields['address'].choices = self.choices


class ReferenceFirstReferenceContactForm(GOVUKForm):
    """
    GOV.UK form for the 2 references: first reference contact details page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    phone_number = forms.CharField(label='Phone number')
    email_address = forms.CharField(label='Email address')

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: first reference contact details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceFirstReferenceContactForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=1).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local,
                                                     reference=1)
            self.fields['phone_number'].initial = reference_record.phone_number
            self.fields['email_address'].initial = reference_record.email

    def clean_phone_number(self):
        """
        Phone number validation
        :return: string
        """
        phone_number = self.cleaned_data['phone_number']
        no_space_phone_number = phone_number.replace(' ', '')
        if phone_number != '':
            if re.match("^(0\d{8,12}|447\d{7,11})$", no_space_phone_number) is None:
                raise forms.ValidationError('TBC')
            if len(no_space_phone_number) > 11:
                raise forms.ValidationError('TBC')
        return phone_number

    def clean_email_address(self):
        """
        Email validation
        :return: string
        """
        email_address = self.cleaned_data['email_address']
        if re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", email_address) is None:
            raise forms.ValidationError('TBC')
        if len(email_address) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return email_address


class SecondReferenceForm(GOVUKForm):
    """
    GOV.UK form for the 2 references: second reference page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    first_name = forms.CharField(label='First name', required=True)
    last_name = forms.CharField(label='Last name', required=True)
    relationship = forms.CharField(label='How do they know you?', help_text='For instance, friend or neighbour',
                                   required=True)
    time_known = TimeKnownField(label='How long have they known you?', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: second reference form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(SecondReferenceForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=2).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local, reference=2)
            self.fields['first_name'].initial = reference_record.first_name
            self.fields['last_name'].initial = reference_record.last_name
            self.fields['relationship'].initial = reference_record.relationship
            self.fields['time_known'].initial = [reference_record.years_known, reference_record.months_known]

    def clean_first_name(self):
        """
        First name validation
        :return: string
        """
        first_name = self.cleaned_data['first_name']
        if re.match("^[A-zÀ-ÿ- ]+$", first_name) is None:
            raise forms.ValidationError('TBC')
        if len(first_name) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return first_name

    def clean_last_name(self):
        """
        Last name validation
        :return: string
        """
        last_name = self.cleaned_data['last_name']
        if re.match("^[A-zÀ-ÿ- ]+$", last_name) is None:
            raise forms.ValidationError('TBC')
        if len(last_name) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return last_name

    def clean_time_known(self):
        """
        Time known validation: reference must be known for 1 year or more
        :return: integer, integer
        """
        years_known = self.cleaned_data['time_known'][1]
        months_known = self.cleaned_data['time_known'][0]
        if months_known != 0:
            reference_known_time = years_known + (months_known / 12)
        elif months_known == 0:
            reference_known_time = years_known
        if reference_known_time < 1:
            raise forms.ValidationError('TBC.')
        return years_known, months_known


class ReferenceSecondReferenceAddressForm(GOVUKForm):
    """
    GOV.UK form for the 2 references: second reference address page for postcode search
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    postcode = forms.CharField(label='Postcode')

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: second reference address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceSecondReferenceAddressForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=2).count() > 0:
            self.fields['postcode'].initial = Reference.objects.get(application_id=self.application_id_local,
                                                                    reference=2).postcode

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        if re.match("^[A-Za-z0-9 ]{5,8}$", postcode) is None:
            raise forms.ValidationError('TBC.')
        return postcode


class ReferenceSecondReferenceAddressManualForm(GOVUKForm):
    """
    GOV.UK form for the 2 references: second reference address page for manual entry
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    street_name_and_number = forms.CharField(label='Address line 1')
    street_name_and_number2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(label='Town or city')
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(label='Postcode')
    country = forms.CharField(label='Country', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: second reference address form for manual entry
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceSecondReferenceAddressManualForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=2).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local, reference=2)
            self.fields['street_name_and_number'].initial = reference_record.street_line1
            self.fields['street_name_and_number2'].initial = reference_record.street_line2
            self.fields['town'].initial = reference_record.town
            self.fields['county'].initial = reference_record.county
            self.fields['postcode'].initial = reference_record.postcode
            self.fields['country'].initial = reference_record.country

    def clean_street_name_and_number(self):
        """
        Street name and number validation
        :return: string
        """
        street_name_and_number = self.cleaned_data['street_name_and_number']
        if len(street_name_and_number) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return street_name_and_number

    def clean_street_name_and_number2(self):
        """
        Street name and number line 2 validation
        :return: string
        """
        street_name_and_number2 = self.cleaned_data['street_name_and_number2']
        if len(street_name_and_number2) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return street_name_and_number2

    def clean_town(self):
        """
        Town validation
        :return: string
        """
        town = self.cleaned_data['town']
        if re.match("^[A-Za-z- ]+$", town) is None:
            raise forms.ValidationError('TBC')
        if len(town) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return town

    def clean_county(self):
        """
        County validation
        :return: string
        """
        county = self.cleaned_data['county']
        if county != '':
            if re.match("^[A-Za-z- ]+$", county) is None:
                raise forms.ValidationError('TBC')
            if len(county) > 100:
                raise forms.ValidationError('Please enter 100 characters or less.')
        return county

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        if re.match("^[A-Za-z0-9 ]{5,8}$", postcode) is None:
            raise forms.ValidationError('TBC')
        return postcode

    def clean_country(self):
        """
        Country validation
        :return: string
        """
        country = self.cleaned_data['country']
        if country != '':
            if re.match("^[A-Za-z- ]+$", country) is None:
                raise forms.ValidationError('TBC')
            if len(country) > 100:
                raise forms.ValidationError('Please enter 100 characters or less.')
        return country


class ReferenceSecondReferenceAddressLookupForm(GOVUKForm):
    """
    GOV.UK form for the 2 references: second reference address page for postcode search results
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    address = forms.ChoiceField(label='Select address', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: second reference address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.choices = kwargs.pop('choices')
        super(ReferenceSecondReferenceAddressLookupForm, self).__init__(*args, **kwargs)
        self.fields['address'].choices = self.choices


class ReferenceSecondReferenceContactForm(GOVUKForm):
    """
    GOV.UK form for the 2 references: second reference contact details page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    phone_number = forms.CharField(label='Phone number')
    email_address = forms.CharField(label='Email address')

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: second reference contct details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceSecondReferenceContactForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=2).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local, reference=2)
            self.fields['phone_number'].initial = reference_record.phone_number
            self.fields['email_address'].initial = reference_record.email

    def clean_phone_number(self):
        """
        Phone number validation
        :return: string
        """
        phone_number = self.cleaned_data['phone_number']
        no_space_phone_number = phone_number.replace(' ', '')
        if phone_number != '':
            if re.match("^(0\d{8,12}|447\d{7,11})$", no_space_phone_number) is None:
                raise forms.ValidationError('TBC')
            if len(no_space_phone_number) > 11:
                raise forms.ValidationError('TBC')
        return phone_number

    def clean_email_address(self):
        """
        Email validation
        :return: string
        """
        email_address = self.cleaned_data['email_address']
        if re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", email_address) is None:
            raise forms.ValidationError('TBC')
        if len(email_address) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return email_address


class ReferenceSummaryForm(GOVUKForm):
    """
    GOV.UK form for the 2 references: summary page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class OtherPeopleGuidanceForm(GOVUKForm):
    """
    GOV.UK form for the People in your home: guidance page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class OtherPeopleAdultQuestionForm(GOVUKForm):
    """
    GOV.UK form for the People in your home: adult question page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    adults_in_home = forms.ChoiceField(label='Does anyone aged 16 or over live or work in your home?', choices=options,
                                       widget=InlineRadioSelect, required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in your home: adult question form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(OtherPeopleAdultQuestionForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        self.fields['adults_in_home'].initial = Application.objects.get(
            application_id=self.application_id_local).adults_in_home


class OtherPeopleAdultDetailsForm(GOVUKForm):
    """
    GOV.UK form for the People in your home: adult details page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    first_name = forms.CharField(label='First name', required=True)
    middle_names = forms.CharField(label='Middle names (if they have any)', required=False)
    last_name = forms.CharField(label='Last name', required=True)
    date_of_birth = SplitDateField(label='Date of birth', help_text='For example, 31 03 1980')
    relationship = forms.CharField(label='How are they related to you?', help_text='For instance, husband or daughter',
                                   required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in your home: adult details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.adult = kwargs.pop('adult')
        super(OtherPeopleAdultDetailsForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if AdultInHome.objects.filter(application_id=self.application_id_local, adult=self.adult).count() > 0:
            adult_record = AdultInHome.objects.get(application_id=self.application_id_local, adult=self.adult)
            self.fields['first_name'].initial = adult_record.first_name
            self.fields['middle_names'].initial = adult_record.middle_names
            self.fields['last_name'].initial = adult_record.last_name
            self.fields['date_of_birth'].initial = [adult_record.birth_day,
                                                    adult_record.birth_month,
                                                    adult_record.birth_year]
            self.fields['relationship'].initial = adult_record.relationship

    def clean_first_name(self):
        """
        First name validation
        :return: string
        """
        first_name = self.cleaned_data['first_name']
        if re.match("^[A-zÀ-ÿ- ]+$", first_name) is None:
            raise forms.ValidationError('TBC')
        if len(first_name) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return first_name

    def clean_middle_names(self):
        """
        Middle names validation
        :return: string
        """
        middle_names = self.cleaned_data['middle_names']
        if middle_names != '':
            if re.match("^[A-zÀ-ÿ- ]+$", middle_names) is None:
                raise forms.ValidationError('TBC')
            if len(middle_names) > 100:
                raise forms.ValidationError('Please enter 100 characters or less.')
        return middle_names

    def clean_last_name(self):
        """
        Last name validation
        :return: string
        """
        last_name = self.cleaned_data['last_name']
        if re.match("^[A-zÀ-ÿ- ]+$", last_name) is None:
            raise forms.ValidationError('TBC')
        if len(last_name) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return last_name

    def clean_date_of_birth(self):
        """
        Date of birth validation (calculate if age is less than 16)
        :return: string
        """
        birth_day = self.cleaned_data['date_of_birth'].day
        birth_month = self.cleaned_data['date_of_birth'].month
        birth_year = self.cleaned_data['date_of_birth'].year
        applicant_dob = date(birth_year, birth_month, birth_day)
        today = date.today()
        age = today.year - applicant_dob.year - ((today.month, today.day) < (applicant_dob.month, applicant_dob.day))
        if age < 16:
            raise forms.ValidationError('TBC')
        return birth_day, birth_month, birth_year


class OtherPeopleAdultDBSForm(GOVUKForm):
    """
    GOV.UK form for the People in your home: adult DBS page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    dbs_certificate_number = forms.IntegerField(label='DBS certificate number',
                                                help_text='12-digit number on their certificate',
                                                required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in your home: adult DBS form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.adult = kwargs.pop('adult')
        self.name = kwargs.pop('name')
        super(OtherPeopleAdultDBSForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if AdultInHome.objects.filter(application_id=self.application_id_local, adult=self.adult).count() > 0:
            adult_record = AdultInHome.objects.get(application_id=self.application_id_local, adult=self.adult)
            self.fields['dbs_certificate_number'].initial = adult_record.dbs_certificate_number

    def clean_dbs_certificate_number(self):
        """
        DBS certificate number validation
        :return: integer
        """
        dbs_certificate_number = self.cleaned_data['dbs_certificate_number']
        if len(str(dbs_certificate_number)) > 12:
            raise forms.ValidationError('TBC')
        if len(str(dbs_certificate_number)) < 12:
            raise forms.ValidationError('TBC')
        return dbs_certificate_number


class OtherPeopleAdultPermissionForm(GOVUKForm):
    """
    GOV.UK form for the People in your home: adult permission page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    permission_declare = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in your home: adult permission form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.adult = kwargs.pop('adult')
        super(OtherPeopleAdultPermissionForm, self).__init__(*args, **kwargs)
        adult = AdultInHome.objects.get(application_id=self.application_id_local, adult=self.adult)
        first_name = adult.first_name
        middle_names = adult.middle_names
        last_name = adult.last_name
        if middle_names != '':
            self.fields['permission_declare'].label = first_name + ' ' + middle_names + ' ' + last_name
        elif middle_names == '':
            self.fields['permission_declare'].label = first_name + ' ' + last_name
        # If information was previously entered, display it on the form
        if AdultInHome.objects.filter(application_id=self.application_id_local, adult=self.adult).count() > 0:
            adult_record = AdultInHome.objects.get(application_id=self.application_id_local, adult=self.adult)
            self.fields['permission_declare'].initial = adult_record.permission_declare


class OtherPeopleChildrenQuestionForm(GOVUKForm):
    """
    GOV.UK form for the People in your home: children question page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    children_in_home = forms.ChoiceField(label='Do you live with any children under 16?', choices=options,
                                         widget=InlineRadioSelect, required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in your home: children question form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(OtherPeopleChildrenQuestionForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        self.fields['children_in_home'].initial = Application.objects.get(
            application_id=self.application_id_local).children_in_home


class OtherPeopleChildrenDetailsForm(GOVUKForm):
    """
    GOV.UK form for the People in your home: children details page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    first_name = forms.CharField(label='First name', required=True)
    middle_names = forms.CharField(label='Middle names (if they have any)', required=False)
    last_name = forms.CharField(label='Last name', required=True)
    date_of_birth = SplitDateField(label='Date of birth', help_text='For example, 31 03 1980')
    relationship = forms.CharField(label='How are they related to you?', help_text='For instance, son or daughter',
                                   required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in your home: children details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.child = kwargs.pop('child')
        super(OtherPeopleChildrenDetailsForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if ChildInHome.objects.filter(application_id=self.application_id_local, child=self.child).count() > 0:
            child_record = ChildInHome.objects.get(application_id=self.application_id_local, child=self.child)
            self.fields['first_name'].initial = child_record.first_name
            self.fields['middle_names'].initial = child_record.middle_names
            self.fields['last_name'].initial = child_record.last_name
            self.fields['date_of_birth'].initial = [child_record.birth_day,
                                                    child_record.birth_month,
                                                    child_record.birth_year]
            self.fields['relationship'].initial = child_record.relationship

    def clean_first_name(self):
        """
        First name validation
        :return: string
        """
        first_name = self.cleaned_data['first_name']
        if re.match("^[A-zÀ-ÿ- ]+$", first_name) is None:
            raise forms.ValidationError('TBC')
        if len(first_name) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return first_name

    def clean_middle_names(self):
        """
        Middle names validation
        :return: string
        """
        middle_names = self.cleaned_data['middle_names']
        if middle_names != '':
            if re.match("^[A-zÀ-ÿ- ]+$", middle_names) is None:
                raise forms.ValidationError('TBC')
            if len(middle_names) > 100:
                raise forms.ValidationError('Please enter 100 characters or less.')
        return middle_names

    def clean_last_name(self):
        """
        Last name validation
        :return: string
        """
        last_name = self.cleaned_data['last_name']
        if re.match("^[A-zÀ-ÿ- ]+$", last_name) is None:
            raise forms.ValidationError('TBC')
        if len(last_name) > 100:
            raise forms.ValidationError('Please enter 100 characters or less.')
        return last_name

    def clean_date_of_birth(self):
        """
        Date of birth validation (calculate if age is more than 16)
        :return: string
        """
        birth_day = self.cleaned_data['date_of_birth'].day
        birth_month = self.cleaned_data['date_of_birth'].month
        birth_year = self.cleaned_data['date_of_birth'].year
        applicant_dob = date(birth_year, birth_month, birth_day)
        today = date.today()
        age = today.year - applicant_dob.year - ((today.month, today.day) < (applicant_dob.month, applicant_dob.day))
        if age >= 16:
            raise forms.ValidationError('TBC')
        return birth_day, birth_month, birth_year


class OtherPeopleApproaching16Form(GOVUKForm):
    """
    GOV.UK form for the People in your home: approaching 16 page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class OtherPeopleNumberOfChildrenForm(GOVUKForm):
    """
    GOV.UK form for the People in your home: number of children page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class OtherPeopleSummaryForm(GOVUKForm):
    """
    GOV.UK form for the People in your home: summary page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class DeclarationDeclarationForm(GOVUKForm):
    """
    GOV.UK form for the Declaration: declaration page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    background_check_declare = forms.BooleanField(label='carry out background checks', required=True)
    inspect_home_declare = forms.BooleanField(label='inspect my home', required=True)
    interview_declare = forms.BooleanField(label='interview me', required=True)
    eyfs_questions_declare = forms.BooleanField(label='ask me questions about the EYFS', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Declaration: declaration form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(DeclarationDeclarationForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            background_check_declare = Application.objects.get(
                application_id=self.application_id_local).background_check_declare
            if background_check_declare is True:
                self.fields['background_check_declare'].initial = '1'
            elif background_check_declare is False:
                self.fields['background_check_declare'].initial = '0'
            inspect_home_declare = Application.objects.get(
                application_id=self.application_id_local).inspect_home_declare
            if inspect_home_declare is True:
                self.fields['inspect_home_declare'].initial = '1'
            elif inspect_home_declare is False:
                self.fields['inspect_home_declare'].initial = '0'
            interview_declare = Application.objects.get(
                application_id=self.application_id_local).interview_declare
            if interview_declare is True:
                self.fields['interview_declare'].initial = '1'
            elif interview_declare is False:
                self.fields['interview_declare'].initial = '0'
            eyfs_questions_declare = Application.objects.get(
                application_id=self.application_id_local).eyfs_questions_declare
            if eyfs_questions_declare is True:
                self.fields['eyfs_questions_declare'].initial = '1'
            elif eyfs_questions_declare is False:
                self.fields['eyfs_questions_declare'].initial = '0'


class DeclarationDeclarationForm2(GOVUKForm):
    """
    GOV.UK form for the Declaration: declaration page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    information_correct_declare = forms.BooleanField(label='the information I have given in this form is correct',
                                                     required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Declaration: declaration form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(DeclarationDeclarationForm2, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            information_correct_declare = Application.objects.get(
                application_id=self.application_id_local).information_correct_declare
            if information_correct_declare is True:
                self.fields['information_correct_declare'].initial = '1'
            elif information_correct_declare is False:
                self.fields['information_correct_declare'].initial = '0'


class DeclarationSummaryForm(GOVUKForm):
    """
    GOV.UK form for the Confirm your details page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True


class PaymentForm(GOVUKForm):
    """
    GOV.UK form for the Payment selection page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    options = (
        ('Credit', 'Credit or debit card'),
        ('PayPal', 'PayPal')
    )
    payment_method = forms.ChoiceField(label='How would you like to pay?', choices=options,
                                       widget=RadioSelect, required=True)


class PaymentDetailsForm(GOVUKForm):
    """
    GOV.UK form for the Payment details page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    options = (
        ('a', 'Alpha'),
        ('b', 'Beta')
    )
    grouped_options = (
        ('First', options),
        ('Second', (('c', 'Gamma'), ('d', 'Delta'))),
    )
    card_type_options = (
        (None, '(Please select)'),
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('american_express', 'American Express'),
        ('maestro', 'Maestro')
    )
    card_type = forms.ChoiceField(label='Card type', choices=card_type_options, required=True)
    card_number = forms.CharField(label='Card number', required=True)
    expiry_date = ExpirySplitDateField(label='Expiry date', required=True, widget=SelectDateWidget)
    cardholders_name = forms.CharField(label="Cardholder's name", required=True)
    card_security_code = forms.IntegerField(label='Card security code',
                                            help_text='3 or 4 digit number on back of card', required=True)

    def clean_card_type(self):
        card_type = self.cleaned_data['card_type']
        if not card_type:
            raise forms.ValidationError('TBC')

    def clean_card_number(self):
        """
        Card number validation
        :return: string
        """
        card_type = self.data['card_type']
        card_number = self.cleaned_data['card_number']
        card_number = re.sub('[ -]+', '', card_number)
        try:
            int(card_number)
        except:
            # At the moment this is a catch all error, in the case of there being multiple error
            # types this must be revisited
            raise forms.ValidationError('TBC')

        if settings.VISA_VALIDATION:
            if card_type == 'visa':
                if re.match("^4[0-9]{12}(?:[0-9]{3})?$", card_number) is None:
                    raise forms.ValidationError('TBC')
        if card_type == 'mastercard':
            if re.match("^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$",
                        card_number) is None:
                raise forms.ValidationError('TBC')
        elif card_type == 'american_express':
            if re.match("^3[47][0-9]{13}$", card_number) is None:
                raise forms.ValidationError('TBC')
        elif card_type == 'maestro':
            if re.match("^(?:5[0678]\d\d|6304|6390|67\d\d)\d{8,15}$", card_number) is None:
                raise forms.ValidationError('TBC')
        return card_number

    def clean_cardholders_name(self):
        """
        Cardholder's name validation
        :return: string
        """
        cardholders_name = self.cleaned_data['cardholders_name']
        if re.match("^[A-Za-z- ]+$", cardholders_name) is None:
            raise forms.ValidationError('TBC')

    def clean_card_security_code(self):
        """
        Card security code validation
        :return: string
        """
        card_security_code = str(self.cleaned_data['card_security_code'])
        if re.match("^[0-9]{3,4}$", card_security_code) is None:
            raise forms.ValidationError('TBC')


class ApplicationSavedForm(GOVUKForm):
    """
    GOV.UK form for the Application saved page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
