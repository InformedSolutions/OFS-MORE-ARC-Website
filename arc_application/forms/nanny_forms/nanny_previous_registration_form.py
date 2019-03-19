from django import forms
from django.conf import settings
from django.forms import ModelForm
from govuk_forms.forms import GOVUKForm
from govuk_forms.widgets import InlineRadioSelect, NumberInput

from ...widgets import ConditionalPostInlineRadioSelect

class PreviousRegistrationDetailsForm(GOVUKForm):
    """
    GOV.UK form for adding details of previous registration
    """
    error_summary_template_name = 'nanny_templates/standard-error-summary.html'
    error_summary_title = 'There was a problem'
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    reveal_conditionally = {'previous_registration': {True: 'individual_id'}}

    choices = (
        (True, 'Yes'),
        (False, 'No')
    )

    previous_registration = forms.ChoiceField(choices=choices,
                                              label='Has the applicant previously registered with Ofsted?',
                                              widget=ConditionalPostInlineRadioSelect, required=True,
                                              error_messages={'required': "Select if the applicant was previously registered with Ofsted"})
    custom_number_input = NumberInput()
    custom_number_input.input_classes = 'form-control form-control-1-4'
    individual_id = forms.IntegerField(label='Individual ID:', widget=custom_number_input, required=True,
                                              error_messages={'required': "Enter individual ID"})
    five_years_in_UK = forms.ChoiceField(choices=choices,
                                         label='Has the applicant lived in England for more than 5 years?',
                                         widget=InlineRadioSelect, required=True,
                                         error_messages={'required': "Select if the applicant lived in England for more than 5 years"})

    def clean(self):
        cleaned_data = self.cleaned_data

        previous_registration = cleaned_data.get('previous_registration', None)
        individual_id = cleaned_data.get('individual_id', None)
        five_years_in_UK = cleaned_data.get('five_years_in_UK', None)

        if previous_registration == 'True' and individual_id == None:
            self.add_error('individual_id', "Enter individual ID")
        if len(str(individual_id)) > 7:
            self.add_error('individual_id', "Individual ID must be fewer than 7 digits")

        return cleaned_data