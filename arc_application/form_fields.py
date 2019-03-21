"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- form_fields.py --
@author: Informed Solutions
"""

import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils.translation import gettext, gettext_lazy as _
from govuk_forms import fields as govf
from govuk_forms import widgets as govw

from .widgets import ExpirySplitDateWidget, TimeKnownSplitDateWidget


class ExpirySplitDateField(forms.MultiValueField):
    """
    This class defines the validation for the month field and also the overall ordering and organisation for the two
    fields
    """
    widget = ExpirySplitDateWidget
    hidden_widget = govw.SplitHiddenDateWidget
    default_error_messages = {
        'invalid': _('TBC.')
    }

    def __init__(self, *args, **kwargs):
        """
        Standard constructor that defines what the month field should do, and which errors should be raised should
        certain events occur
        :param args: Standard arguments parameter
        :param kwargs: Standard key word arguments parameter
        """
        month_bounds_error = gettext('Month should be between 1 and 12.')
        self.current_year = now().year
        # Field definition
        self.fields = [
            forms.IntegerField(min_value=1, max_value=12, error_messages={
                'min_value': month_bounds_error,
                'max_value': month_bounds_error,
                'invalid': gettext('TBC.')
            }),
            # Uses a clean year field defined above
            govf.YearField(min_value=self.current_year, max_value=None),
        ]

        super().__init__(self.fields, *args, **kwargs)

    def compress(self, data_list):
        """
        Uses compress as there are multiple values (compress is a replacement for clean in these cases
        :param data_list: The object containing each of the values
        :return: Returns the cleaned value object
        """
        if data_list:
            try:
                if any(item in self.empty_values for item in data_list):
                    raise ValueError
                return data_list[1], data_list[0]
            except ValueError:
                raise forms.ValidationError(self.error_messages['invalid'], code='invalid')
        return None

    def widget_attrs(self, widget):
        """
        Populates the attributes of the widget with the values defined in the original widget creation
        :param widget: The widget to have its parameters populated
        :return: returns the attributes
        """
        attrs = super().widget_attrs(widget)
        if not isinstance(widget, ExpirySplitDateWidget):
            return attrs
        for subfield, subwidget in zip(self.fields, widget.widgets):
            if subfield.min_value is not None:
                subwidget.attrs['min'] = subfield.min_value
            if subfield.max_value is not None:
                subwidget.attrs['max'] = subfield.max_value
        return attrs


class TimeKnownField(forms.MultiValueField):
    """
    Class that defines the field type used for both month and years in the TimeKnownWidget
    """
    widget = TimeKnownSplitDateWidget
    hidden_widget = govw.SplitHiddenDateWidget
    default_error_messages = {
        'invalid': _('Enter a valid date.')
    }

    def __init__(self, *args, **kwargs):
        """
        The contructor defines each field for the object, the errors it can raise and the resultant error text should
        an error be returned
        :param args: Standard arguments parameter
        :param kwargs: Standard key word arguments parameter
        """
        month_bounds_error = gettext('The number of months should be maximum 11.')
        year_bounds_error = gettext('The number of years should be maximum 100')

        self.fields = [
            forms.IntegerField(max_value=100, error_messages={
                'min_value': year_bounds_error,
                'max_value': year_bounds_error,
                'invalid': gettext('Enter number of years as a number.')
            }),
            forms.IntegerField(max_value=11, error_messages={
                'min_value': month_bounds_error,
                'max_value': month_bounds_error,
                'invalid': gettext('Enter number of months as a number.')
            })
        ]

        super().__init__(self.fields, *args, **kwargs)

    def compress(self, data_list):
        """
        Compresses the resultant data list into a single tuple for returning to wherever the result is called
        :param data_list: The list of field inputs
        :return: Atuple containing the amount of months and years known in the correct order
        """
        if data_list:
            try:
                if any(item in self.empty_values for item in data_list):
                    raise ValueError
                return data_list[1], data_list[0]
            except ValueError:
                raise forms.ValidationError(self.error_messages['invalid'], code='invalid')
        return None

    def widget_attrs(self, widget):
        """
        Populates the attributes of the widget with the values defined in the original widget creation
        :param widget: The widget to have its parameters populated
        :return: returns the attributes
        """
        attrs = super().widget_attrs(widget)
        if not isinstance(widget, ExpirySplitDateWidget):
            return attrs
        for subfield, subwidget in zip(self.fields, widget.widgets):
            if subfield.min_value is not None:
                subwidget.attrs['min'] = subfield.min_value
            if subfield.max_value is not None:
                subwidget.attrs['max'] = subfield.max_value
        return attrs


class CustomSplitDateField(govf.SplitDateField):
    """
    Extends govuk_forms.fields.SplitDateField to:
    * allow all child field options and error messages to be customised (prefix with "day_", "month_" or "year_")
    * use different default bounds and error messages
    * introduce finer-grained error messages for date validation
    * allow 4-digit years to be required
    """

    # Sentinel which can be passed in for min_value or max_value, triggering a different error message than if a fixed
    # date was passed in
    TODAY = object()

    default_error_messages = {
        'invalid': 'Enter a real date',
        'required': 'Enter the date, including the day, month and year',
        'incomplete': 'Enter the date, including the day, month and year',
        'min_value': 'Date must be after 1 Jan 1900',
        'max_value': "Date must be before today's date",
        'min_today': 'Date must be in the future',
        'max_today': 'Date must be in the past',
        'short_year': 'The year is too short',
    }

    def __init__(self, *args, **kwargs):

        day_args = self._pop_prefixed_kwargs(kwargs, 'day_')
        day_options = {
            'min_value': 1,
            'max_value': 31,
            'error_messages': {
                'min_value': 'Day must be between 1 and 31',
                'max_value': 'Day must be between 1 and 31',
                'invalid': 'Enter day as a number',
            },
        }
        day_options.update(day_args)

        month_args = self._pop_prefixed_kwargs(kwargs, 'month_')
        month_options = {
            'min_value': 1,
            'max_value': 12,
            'error_messages': {
                'min_value': 'Month must be between 1 and 12',
                'max_value': 'Month must be between 1 and 12',
                'invalid': 'Enter month as a number',
            },
        }
        month_options.update(month_args)

        year_args = self._pop_prefixed_kwargs(kwargs, 'year_')
        current_year = datetime.date.today().year
        century = 100 * (current_year // 100)
        era_boundary = current_year - century
        year_options = {
            'min_value': 2000,
            'max_value': current_year,
            'era_boundary': era_boundary,
            'error_messages': {
                'min_value': 'Year must be between 2000 and the current year',
                'max_value': 'Year must be between 2000 and the current year',
                'invalid': 'Enter year as a number',
                'short_year': 'Enter year in long year format.'
            },
        }
        year_options.update(year_args)

        options = {
            'min_value': datetime.date(1900, 1, 1),
            'max_value': self.TODAY,
            'required': False,
            'allow_short_year': True,
        }
        options.update(**kwargs)

        self.min_value = options.pop('min_value')
        self.max_value = options.pop('max_value')
        self.required = options.pop('required')
        self.allow_short_year = options.pop('allow_short_year')

        self.fields = [
            forms.IntegerField(**day_options),
            forms.IntegerField(**month_options)
        ]

        if self.allow_short_year:
            self.fields.append(govf.YearField(**year_options))
        else:
            year_options.pop('era_boundary')
            self.fields.append(NoShortYearField(**year_options))

        super(govf.SplitDateField, self).__init__(self.fields, *args, **options)

    def compress(self, data_list):
        """
        `compress` is used in place of `clean` for subclasses of MultiValueField
        """
        if not data_list:
            return None

        if any(item in self.empty_values for item in data_list):
            if self.required:
                raise forms.ValidationError(self.error_messages['required'], code='required')
            else:
                return None

        try:
            date_compressed = datetime.date(data_list[2], data_list[1], data_list[0])
        except ValueError:
            raise forms.ValidationError(self.error_messages['invalid'], code='invalid')

        if self.min_value is not None:
            if self.min_value is self.TODAY and date_compressed < datetime.date.today():
                raise forms.ValidationError(self.error_messages['min_today'], code='min_today')
            elif self.min_value is not self.TODAY and date_compressed < self.min_value:
                raise forms.ValidationError(self.error_messages['min_value'], code='min_value')

        if self.max_value is not None:
            if self.max_value is self.TODAY and date_compressed > datetime.date.today():
                raise forms.ValidationError(self.error_messages['max_today'], code='max_today')
            elif self.max_value is not self.TODAY and date_compressed < self.max_value:
                raise forms.ValidationError(self.error_messages['max_value'], code='max_value')

        return date_compressed

    def _pop_prefixed_kwargs(self, kwarg_dict, prefix):
        result = {}
        dict_copy = dict(kwarg_dict)
        for k, v in dict_copy.items():
            if k.startswith(prefix):
                result[k[len(prefix):]] = kwarg_dict.pop(k)
        return result


class NoShortYearField(forms.IntegerField):
    default_error_messages = {
        'short_year': _('Enter year in long year format.'),
    }

    def __init__(self, **kwargs):
        self.current_year = now().year
        options = {
            'min_value': 1900,
            'max_value': self.current_year,
            'error_messages': {
                'invalid': gettext('Enter year as a number.'),
                'short_year': 'Enter year in long year format.'
            }
        }
        options.update(kwargs)
        super().__init__(**options)

    def clean(self, value):
        value = self.to_python(value)
        if isinstance(value, int) and value < 1000:
            raise ValidationError(self.error_messages['short_year'], code='short_year')
        return super().clean(value)
