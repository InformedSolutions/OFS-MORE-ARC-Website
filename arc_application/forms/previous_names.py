from collections import OrderedDict
from datetime import date

from django import forms
from govuk_forms.forms import GOVUKForm
from .. import form_fields


class PersonPreviousNameForm(GOVUKForm):
    """
    Form for adding previous addresses to childminder/nanny applicants, people in the home, children etc.
    """

    ERROR_MESSAGE_FIRST_NAME_BLANK = 'You must enter a first name'
    ERROR_MESSAGE_LAST_NAME_BLANK = 'You must enter a last name'

    ERROR_MESSAGE_DATE_BLANK = 'Enter the date, including the month and year'
    ERROR_MESSAGE_DAY_OUT_OF_RANGE = 'Day must be between 1 and 31'
    ERROR_MESSAGE_MONTH_OUT_OF_RANGE = 'Month must be between 1 and 12'
    ERROR_MESSAGE_START_YEAR_BEFORE_1900 = 'Start date must be after 1900'
    ERROR_MESSAGE_END_YEAR_BEFORE_1900 = 'End date must be after 1900'
    ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS = 'Enter the whole year (4 digits)'
    ERROR_MESSAGE_INVALID_DATE = 'Enter a real date'
    ERROR_MESSAGE_NON_NUMERIC = 'Use numbers for the date'

    ERROR_MESSAGE_START_DATE_AFTER_CURRENT_DATE = 'Start date must be today or in the past'
    ERROR_MESSAGE_START_DATE_AFTER_END_DATE = 'Start date must be before the end date'

    ERROR_MESSAGE_END_DATE_AFTER_CURRENT_DATE = 'End date must be before today or in the past'
    ERROR_MESSAGE_END_DATE_BEFORE_START_DATE = 'End date must be after the start date'

    auto_replace_widgets = True
    field_label_classes = 'form-label-bold'
    error_summary_title = 'There was a problem'

    previous_name_id = forms.CharField(
        widget=forms.widgets.HiddenInput,
        required=False,
    )

    first_name = forms.CharField(
        label='First name',
        max_length=200,
        required=True,
        error_messages={'required': 'You must enter a first name'},
    )
    middle_names = forms.CharField(
        label='Middle names',
        max_length=200,
        required=False
    )
    last_name = forms.CharField(
        label='Last name',
        max_length=200,
        required=True,
        error_messages={'required': 'You must enter a last name'},
    )
    start_date = form_fields.CustomSplitDateField(
        label='Start date',
        required=True,
        help_text='For example, 31 3 2010',
        min_value=None,
        max_value=form_fields.CustomSplitDateField.TODAY,
        allow_short_year=False,
        error_messages={'required': ERROR_MESSAGE_DATE_BLANK,
                        'incomplete': ERROR_MESSAGE_DATE_BLANK,
                        'max_today': ERROR_MESSAGE_START_DATE_AFTER_CURRENT_DATE,
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
        year_error_messages={'min_value': ERROR_MESSAGE_START_YEAR_BEFORE_1900,
                             'invalid': ERROR_MESSAGE_NON_NUMERIC},
    )
    end_date = form_fields.CustomSplitDateField(
        label='End date',
        required=True,
        help_text='For example, 31 3 2019',
        min_value=None,
        max_value=form_fields.CustomSplitDateField.TODAY,
        allow_short_year=False,
        error_messages={'required': ERROR_MESSAGE_DATE_BLANK,
                        'incomplete': ERROR_MESSAGE_DATE_BLANK,
                        'max_today': ERROR_MESSAGE_END_DATE_AFTER_CURRENT_DATE,
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
        year_error_messages={'min_value': ERROR_MESSAGE_END_YEAR_BEFORE_1900,
                             'invalid': ERROR_MESSAGE_NON_NUMERIC},
    )

    def clean(self):
        super().clean()

        # check start date is after end date
        start_date = self.cleaned_data.get('start_date', None)
        end_date = self.cleaned_data.get('end_date', None)
        if start_date and end_date and end_date < start_date:
            self.add_error('start_date', self.ERROR_MESSAGE_START_DATE_AFTER_END_DATE)
            self.add_error('end_date', self.ERROR_MESSAGE_END_DATE_BEFORE_START_DATE)

        # de-duplicate error messages for each field
        for field, errors in self.errors.items():
            dedup = OrderedDict([(k, None) for k in errors])
            self.errors[field] = list(dedup.keys())

