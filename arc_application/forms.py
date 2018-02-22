"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- forms.py --

@author: Informed Solutions
"""

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserModel
from govuk_forms.forms import GOVUKForm

from . import custom_field_widgets

from .models import ArcReview
from .views import has_group, authenticate, capfirst


class CheckBox(GOVUKForm):
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    information_correct_declare = forms.BooleanField(label='This information is correct')


class PersonalDetailsForm(GOVUKForm):
    # customisations:
    auto_replace_widgets = True
    reveal_conditionally = {
        'name_correct_declare': {True: 'name_correct_comments'},
        'dateofbirth_correct_declare': {True: 'dateofbirth_correct_comments'},
        'homeaddress_correct_declare': {True: 'homeaddress_correct_comments'},
        'childcarelocation_correct_declare': {True: 'childcarelocation_correct_comments'},
    }

    field_label_classes = 'form-label-bold'
    name_correct_declare = forms.BooleanField(label='This information is correct', widget=custom_field_widgets.CustomCheckboxInput)
    name_correct_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)
    dateofbirth_correct_declare = forms.BooleanField(label='This information is correct', widget=custom_field_widgets.CustomCheckboxInput)
    dateofbirth_correct_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)
    homeaddress_correct_declare = forms.BooleanField(label='This information is correct', widget=custom_field_widgets.CustomCheckboxInput)
    homeaddress_correct_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)
    childcarelocation_correct_declare = forms.BooleanField(label='This information is correct', widget=custom_field_widgets.CustomCheckboxInput)
    childcarelocation_correct_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    checkboxes = [(name_correct_declare,'name'), (dateofbirth_correct_declare,'dateofbirth'),
                  (homeaddress_correct_declare,'homeaddress'),(childcarelocation_correct_declare,'childcarelocation')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                                'aria-controls': box[1],
                                                'aria-expanded': 'false'},)


class CommentsForm(GOVUKForm):
    """
    GOV.UK form for the Your login and contact details: email page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    comments = forms.CharField(label='Comments', required=False, widget=forms.TextInput(attrs={'size': 80}))

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your login and contact details: email form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(CommentsForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if ArcReview.objects.filter(application_id=self.application_id_local).count() > 0:
            rev = ArcReview.objects.get(application_id=self.application_id_local)
            self.fields['comments'].initial = rev.comments

    def clean_comments(self):
        comments = self.cleaned_data['comments']
        # RegEx for valid e-mail addresses

        return comments

