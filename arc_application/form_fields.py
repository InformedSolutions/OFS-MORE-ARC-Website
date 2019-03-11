"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- form_fields.py --
@author: Informed Solutions
"""

from django import forms
from django.utils.timezone import now
from django.utils.translation import gettext, gettext_lazy as _
from govuk_forms import widgets as gov

from arc_application.widgets import ExpirySplitDateWidget, TimeKnownSplitDateWidget


class YearField(forms.IntegerField):
    """
    In integer field that accepts years between 1900 and now
    Allows 2-digit year entry which is converted depending on the `era_boundary`
    """

    def __init__(self, era_boundary=None, **kwargs):
        """
        When initialised, this field object will create attributes for later validation base of the current time and
        year, error messages and field options are specified here.
        :param era_boundary: If supplied, will limit how far back a user cna enter without raising an error
        :param kwargs: Any other key word arguments passed during the implementation of the class
        """
        self.current_year = now().year
        self.century = 100 * (self.current_year // 100)
        if era_boundary is None:
            # 2-digit dates are a minimum of 10 years ago by default
            era_boundary = self.current_year - self.century - 10
        self.era_boundary = era_boundary
        bounds_error = gettext('TBC') % {
            'current_year': self.current_year
        }
        options = {
            'min_value': self.current_year,
            'error_messages': {
                'min_value': bounds_error,
                'invalid': gettext('TBC'),
            }
        }
        options.update(kwargs)
        super().__init__(**options)

    def clean(self, value):
        """
        This will clean the two year value enetered into the field in order to ensure the value entered is in the write
        century, for example, 68 will be changed to 1968 rather the 2068 as the latter has not occured yet
        :param value:The value object obtained from the form
        :return:This returns the cleaned value object (after cleaning specified above
        """
        value = self.to_python(value)
        if isinstance(value, int) and value < 100:
            if value > self.era_boundary:
                value += self.century - 100
            else:
                value += self.century
        return super().clean(value)


class ExpirySplitDateField(forms.MultiValueField):
    """
    This class defines the validation for the month field and also the overall ordering and organisation for the two
    fields
    """
    widget = ExpirySplitDateWidget
    hidden_widget = gov.SplitHiddenDateWidget
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

        # Field definition
        self.fields = [
            forms.IntegerField(min_value=1, max_value=12, error_messages={
                'min_value': month_bounds_error,
                'max_value': month_bounds_error,
                'invalid': gettext('TBC.')
            }),
            # Uses a clean year field defined above
            YearField(),
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
    hidden_widget = gov.SplitHiddenDateWidget
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


