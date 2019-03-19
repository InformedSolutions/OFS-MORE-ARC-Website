import re
from collections import OrderedDict

from django import forms
from django.conf import settings
from govuk_forms.forms import GOVUKForm

from .. import form_fields


class PreviousAddressEntryForm(GOVUKForm):
    """
    GOV.UK form for the Your children's address page for postcode search
    """
    ERROR_MESSAGE_POSTCODE_NOT_ENTERED = 'Please enter your postcode'
    ERROR_MESSAGE_POSTCODE_INVALID = 'Please enter a valid postcode'

    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    error_summary_title = 'There was a problem on this page'

    postcode = forms.CharField(label='Postcode', error_messages={'required': 'Please enter your postcode'})

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        postcode_no_space = postcode.replace(" ", "")
        postcode_uppercase = postcode_no_space.upper()
        if re.match(settings.REGEX['POSTCODE_UPPERCASE'], postcode_uppercase) is None:
            raise forms.ValidationError(self.ERROR_MESSAGE_POSTCODE_INVALID)
        return postcode_uppercase


class PreviousAddressSelectForm(GOVUKForm):

    # Address validation messages
    ERROR_MESSAGE_ADDRESS_BLANK = 'Please select your address'

    # Moved in/out date validation messages
    ERROR_MESSAGE_DATE_BLANK = 'Enter the date, including the month and year'
    ERROR_MESSAGE_DAY_OUT_OF_RANGE = 'Day must be between 1 and 31'
    ERROR_MESSAGE_MONTH_OUT_OF_RANGE = 'Month must be between 1 and 12'
    ERROR_MESSAGE_MOVED_IN_YEAR_BEFORE_1900 = 'Date moved in must be after 1900'
    ERROR_MESSAGE_MOVED_OUT_YEAR_BEFORE_1900 = 'Date you moved out must be after 1900'
    ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS = 'Enter the whole year (4 digits)'
    ERROR_MESSAGE_INVALID_DATE = 'Enter a real date'
    ERROR_MESSAGE_NON_NUMERIC = 'Use numbers for the date'

    ERROR_MESSAGE_MOVED_IN_DATE_AFTER_CURRENT_DATE = 'Date moved in must be today or in the past'
    ERROR_MESSAGE_MOVED_IN_DATE_AFTER_MOVED_OUT_DATE = 'Date you moved in must be before date you moved out'

    ERROR_MESSAGE_MOVED_OUT_DATE_AFTER_CURRENT_DATE = 'Date you moved out must be today or in the past'
    ERROR_MESSAGE_MOVED_OUT_DATE_BEFORE_MOVED_IN_DATE = 'Date you moved out must be after the date you moved in'

    auto_replace_widgets = True
    field_label_classes = 'form-label-bold'
    error_summary_title = 'There was a problem on this page'

    address = forms.ChoiceField(
        label='Select address',
        required=True,
        error_messages={'required': ERROR_MESSAGE_ADDRESS_BLANK}
    )
    moved_in_date = form_fields.CustomSplitDateField(
        label='Moved in',
        required=True,
        help_text='For example, 31 03 1980',
        min_value=None,
        max_value=form_fields.CustomSplitDateField.TODAY,
        allow_short_year=False,
        error_messages={'required': ERROR_MESSAGE_DATE_BLANK,
                        'incomplete': ERROR_MESSAGE_DATE_BLANK,
                        'max_today': ERROR_MESSAGE_MOVED_IN_DATE_AFTER_CURRENT_DATE,
                        'invalid': ERROR_MESSAGE_INVALID_DATE,
                        'short_year': ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS},
        day_error_messages={'min_value': ERROR_MESSAGE_DAY_OUT_OF_RANGE,
                            'max_value': ERROR_MESSAGE_DAY_OUT_OF_RANGE,
                            'invalid': ERROR_MESSAGE_NON_NUMERIC},
        month_error_messages={'min_value': ERROR_MESSAGE_MONTH_OUT_OF_RANGE,
                              'max_value': ERROR_MESSAGE_MONTH_OUT_OF_RANGE,
                              'invalid': ERROR_MESSAGE_NON_NUMERIC},
        year_min_value=1900,
        year_max_value=None,
        year_error_messages={'min_value': ERROR_MESSAGE_MOVED_IN_YEAR_BEFORE_1900,
                             'invalid': ERROR_MESSAGE_NON_NUMERIC},
    )
    moved_out_date = form_fields.CustomSplitDateField(
        label='Moved out',
        required=True,
        help_text='For example, 31 03 1980',
        min_value=None,
        max_value=form_fields.CustomSplitDateField.TODAY,
        allow_short_year=False,
        error_messages={'required': ERROR_MESSAGE_DATE_BLANK,
                        'incomplete': ERROR_MESSAGE_DATE_BLANK,
                        'max_today': ERROR_MESSAGE_MOVED_OUT_DATE_AFTER_CURRENT_DATE,
                        'invalid': ERROR_MESSAGE_INVALID_DATE,
                        'short_year': ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS},
        day_error_messages={'min_value': ERROR_MESSAGE_DAY_OUT_OF_RANGE,
                            'max_value': ERROR_MESSAGE_DAY_OUT_OF_RANGE,
                            'invalid': ERROR_MESSAGE_NON_NUMERIC},
        month_error_messages={'min_value': ERROR_MESSAGE_MONTH_OUT_OF_RANGE,
                              'max_value': ERROR_MESSAGE_MONTH_OUT_OF_RANGE,
                              'invalid': ERROR_MESSAGE_NON_NUMERIC},
        year_min_value=1900,
        year_max_value=None,
        year_error_messages={'min_value': ERROR_MESSAGE_MOVED_OUT_YEAR_BEFORE_1900,
                             'invalid': ERROR_MESSAGE_NON_NUMERIC},
    )

    def __init__(self, *args, **kwargs):
        """
        Configure available address choices via passed kwarg.
        """
        self.choices = kwargs.pop('choices')
        super(PreviousAddressSelectForm, self).__init__(*args, **kwargs)
        self.fields['address'].choices = self.choices

    def clean(self):
        super().clean()

        # check start date is after end date
        start_date = self.cleaned_data.get('moved_in_date', None)
        end_date = self.cleaned_data.get('moved_out_date', None)
        if start_date and end_date and end_date < start_date:
            self.add_error('moved_in_date', self.ERROR_MESSAGE_MOVED_IN_DATE_AFTER_MOVED_OUT_DATE)
            self.add_error('moved_out_date', self.ERROR_MESSAGE_MOVED_OUT_DATE_BEFORE_MOVED_IN_DATE)

        # de-duplicate error messages for each field
        for field, errors in self.errors.items():
            dedup = OrderedDict([(k, None) for k in errors])
            self.errors[field] = list(dedup.keys())


class PreviousAddressManualForm(GOVUKForm):
    """
    Form for adding previous addresses to childminder/nanny applicants, people in the home, children etc.
    """

    # Manual address entry field validation messages
    ERROR_MESSAGE_STREET_LINE_1_BLANK = 'Please enter the first line of your address'
    ERROR_MESSAGE_STREET_LINE_1_TOO_LONG = 'The first line of your address must be under 50 characters long'
    ERROR_MESSAGE_STREET_LINE_2_TOO_LONG = 'The second line of your address must be under 50 characters long'
    ERROR_MESSAGE_TOWN_BLANK = 'Please enter the name of the town or city'
    ERROR_MESSAGE_TOWN_INVALID = 'Please spell out the name of the town or city using letters'
    ERROR_MESSAGE_TOWN_TOO_LONG = 'The name of the town or city must be under 50 characters long'
    ERROR_MESSAGE_COUNTY_INVALID = 'Please spell out the name of the county using letters'
    ERROR_MESSAGE_COUNTY_TOO_LONG = 'The name of the county must be under 50 characters long'
    ERROR_MESSAGE_POSTCODE_BLANK = 'Please enter your postcode'
    ERROR_MESSAGE_POSTCODE_INVALID = 'Please enter a valid postcode'

    # Moved in/out date validation messages
    ERROR_MESSAGE_DATE_BLANK = 'Enter the date, including the month and year'
    ERROR_MESSAGE_DAY_OUT_OF_RANGE = 'Day must be between 1 and 31'
    ERROR_MESSAGE_MONTH_OUT_OF_RANGE = 'Month must be between 1 and 12'
    ERROR_MESSAGE_MOVED_IN_YEAR_BEFORE_1900 = 'Date moved in must be after 1900'
    ERROR_MESSAGE_MOVED_OUT_YEAR_BEFORE_1900 = 'Date you moved out must be after 1900'
    ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS = 'Enter the whole year (4 digits)'
    ERROR_MESSAGE_INVALID_DATE = 'Enter a real date'
    ERROR_MESSAGE_NON_NUMERIC = 'Use numbers for the date'

    ERROR_MESSAGE_MOVED_IN_DATE_AFTER_CURRENT_DATE = 'Date moved in must be today or in the past'
    ERROR_MESSAGE_MOVED_IN_DATE_AFTER_MOVED_OUT_DATE = 'Date you moved in must be before date you moved out'

    ERROR_MESSAGE_MOVED_OUT_DATE_AFTER_CURRENT_DATE = 'Date you moved out must be today or in the past'
    ERROR_MESSAGE_MOVED_OUT_DATE_BEFORE_MOVED_IN_DATE = 'Date you moved out must be after the date you moved in'

    auto_replace_widgets = True
    field_label_classes = 'form-label-bold'
    error_summary_title = 'There was a problem on this page'

    street_line1 = forms.CharField(
        label='Address line 1',
        required=True,
        error_messages={'required': ERROR_MESSAGE_STREET_LINE_1_BLANK}
    )

    street_line2 = forms.CharField(
        label='Address line 2',
        required=False
    )

    town = forms.CharField(
        label='Town or city',
        required=True,
        error_messages={'required': ERROR_MESSAGE_TOWN_BLANK}
    )

    county = forms.CharField(
        label='County (optional)',
        required=False
    )

    postcode = forms.CharField(
        label='Postcode',
        required=True,
        error_messages={'required': ERROR_MESSAGE_POSTCODE_BLANK}
    )

    moved_in_date = form_fields.CustomSplitDateField(
        label='Moved in',
        required=True,
        help_text='For example, 31 3 2012',
        min_value=None,
        max_value=form_fields.CustomSplitDateField.TODAY,
        allow_short_year=False,
        error_messages={'required': ERROR_MESSAGE_DATE_BLANK,
                        'incomplete': ERROR_MESSAGE_DATE_BLANK,
                        'max_today': ERROR_MESSAGE_MOVED_IN_DATE_AFTER_CURRENT_DATE,
                        'invalid': ERROR_MESSAGE_INVALID_DATE,
                        'short_year': ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS},
        day_error_messages={'min_value': ERROR_MESSAGE_DAY_OUT_OF_RANGE,
                            'max_value': ERROR_MESSAGE_DAY_OUT_OF_RANGE,
                            'invalid': ERROR_MESSAGE_NON_NUMERIC},
        month_error_messages={'min_value': ERROR_MESSAGE_MONTH_OUT_OF_RANGE,
                              'max_value': ERROR_MESSAGE_MONTH_OUT_OF_RANGE,
                              'invalid': ERROR_MESSAGE_NON_NUMERIC},
        year_min_value=1900,
        year_max_value=None,
        year_error_messages={'min_value': ERROR_MESSAGE_MOVED_IN_YEAR_BEFORE_1900,
                             'invalid': ERROR_MESSAGE_NON_NUMERIC},
    )
    moved_out_date = form_fields.CustomSplitDateField(
        label='Moved out',
        required=True,
        help_text='For example, 31 3 2012',
        min_value=None,
        max_value=form_fields.CustomSplitDateField.TODAY,
        allow_short_year=False,
        error_messages={'required': ERROR_MESSAGE_DATE_BLANK,
                        'incomplete': ERROR_MESSAGE_DATE_BLANK,
                        'max_today': ERROR_MESSAGE_MOVED_OUT_DATE_AFTER_CURRENT_DATE,
                        'invalid': ERROR_MESSAGE_INVALID_DATE,
                        'short_year': ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS},
        day_error_messages={'min_value': ERROR_MESSAGE_DAY_OUT_OF_RANGE,
                            'max_value': ERROR_MESSAGE_DAY_OUT_OF_RANGE,
                            'invalid': ERROR_MESSAGE_NON_NUMERIC},
        month_error_messages={'min_value': ERROR_MESSAGE_MONTH_OUT_OF_RANGE,
                              'max_value': ERROR_MESSAGE_MONTH_OUT_OF_RANGE,
                              'invalid': ERROR_MESSAGE_NON_NUMERIC},
        year_min_value=1900,
        year_max_value=None,
        year_error_messages={'min_value': ERROR_MESSAGE_MOVED_OUT_YEAR_BEFORE_1900,
                             'invalid': ERROR_MESSAGE_NON_NUMERIC},
    )

    def __init__(self, *args, **kwargs):
        """
        Setup initial data for the manual form
        """
        record = kwargs.pop('record', None)
        super().__init__(*args, **kwargs)

        if record:
            self.fields['street_line1'].initial = record.street_line1
            self.fields['street_line2'].initial = record.street_line2
            self.fields['town'].initial = record.town
            self.fields['county'].initial = record.county
            self.fields['postcode'].initial = record.postcode
            self.fields['moved_in_date'].initial = record.moved_in_date
            self.fields['moved_out_date'].initial = record.moved_out_date


    def clean(self):
        super().clean()

        # check start date is after end date
        start_date = self.cleaned_data.get('moved_in_date', None)
        end_date = self.cleaned_data.get('moved_out_date', None)
        if start_date and end_date and end_date < start_date:
            self.add_error('moved_in_date', self.ERROR_MESSAGE_MOVED_IN_DATE_AFTER_MOVED_OUT_DATE)
            self.add_error('moved_out_date', self.ERROR_MESSAGE_MOVED_OUT_DATE_BEFORE_MOVED_IN_DATE)

        # de-duplicate error messages for each field
        for field, errors in self.errors.items():
            dedup = OrderedDict([(k, None) for k in errors])
            self.errors[field] = list(dedup.keys())

    def clean_street_line1(self):
        """
        Street name and number validation
        :return: string
        """
        street_line1 = self.cleaned_data['street_line1']
        if len(street_line1) > 50:
            raise forms.ValidationError(self.ERROR_MESSAGE_STREET_LINE_1_TOO_LONG)
        return street_line1

    def clean_street_line2(self):
        """
        Street name and number line 2 validation
        :return: string
        """
        street_line2 = self.cleaned_data['street_line2']
        if len(street_line2) > 50:
            raise forms.ValidationError(self.ERROR_MESSAGE_STREET_LINE_2_TOO_LONG)
        return street_line2

    def clean_town(self):
        """
        Town validation
        :return: string
        """
        town = self.cleaned_data['town']
        if re.match(settings.REGEX['TOWN'], town) is None:
            raise forms.ValidationError(self.ERROR_MESSAGE_TOWN_INVALID)
        if len(town) > 50:
            raise forms.ValidationError(self.ERROR_MESSAGE_TOWN_TOO_LONG)
        return town

    def clean_county(self):
        """
        County validation
        :return: string
        """
        county = self.cleaned_data['county']
        if county != '':
            if re.match(settings.REGEX['COUNTY'], county) is None:
                raise forms.ValidationError(self.ERROR_MESSAGE_COUNTY_INVALID)
            if len(county) > 50:
                raise forms.ValidationError(self.ERROR_MESSAGE_COUNTY_TOO_LONG)
        return county

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        postcode_no_space = postcode.replace(" ", "")
        postcode_uppercase = postcode_no_space.upper()
        if re.match(settings.REGEX['POSTCODE_UPPERCASE'], postcode_uppercase) is None:
            raise forms.ValidationError(self.ERROR_MESSAGE_POSTCODE_INVALID)
        return postcode_uppercase
