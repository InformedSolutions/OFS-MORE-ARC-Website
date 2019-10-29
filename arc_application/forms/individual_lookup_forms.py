from django import forms
from govuk_forms.forms import GOVUKForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from datetime import datetime

from .. import form_fields


class IndividualLookupSearchForm(GOVUKForm):
    ERROR_MESSAGE_INVALID_DATE = 'Enter a real date'
    
    auto_replace_widgets = True
    field_label_classes = 'form-label-bold'

    forenames = forms.CharField(
        label='Forenames',
        max_length=100,
        required=False
    )
    last_name = forms.CharField(
        label='Last name',
        max_length=100,
        required=False
    )
    day = forms.IntegerField(required=False)
    month = forms.IntegerField(required=False)
    year = forms.IntegerField(required=False)
    street = forms.CharField(
        label='Street',
        max_length=100,
        required=False
    )
    town = forms.CharField(
        label='Town',
        max_length=100,
        required=False
    )
    postcode = forms.CharField(
        label='Postcode',
        max_length=100,
        required=False
    )
    
    def clean(self):
        day = self.cleaned_data.get("day")
        month = self.cleaned_data.get("month")
        year = self.cleaned_data.get("year")
        error_messages = {}

        if year:
            if year < 1900:
                error_messages['invalid_date'] = self.ERROR_MESSAGE_INVALID_DATE
        
        if month:
            if month < 1 or month > 12:
                error_messages['invalid_date'] = self.ERROR_MESSAGE_INVALID_DATE

        if day:
            if day < 1 or day > 31:
                error_messages['invalid_date'] = self.ERROR_MESSAGE_INVALID_DATE
        
        if error_messages:
            raise ValidationError(''.join(['%s' % (value) for (key, value) in error_messages.items()]))
    
        