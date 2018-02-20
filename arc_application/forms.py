"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- forms.py --

@author: Informed Solutions
"""

from govuk_forms.forms import GOVUKForm
from django import forms
from govuk_forms.widgets import CheckboxSelectMultiple, InlineRadioSelect, RadioSelect
from govuk_forms.fields import SplitDateField


class CheckBox(GOVUKForm):
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    information_correct_declare = forms.BooleanField(label='This information is correct')


