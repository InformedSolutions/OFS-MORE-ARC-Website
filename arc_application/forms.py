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


class LogInDetailsForm(GOVUKForm):
    # customisations:
    auto_replace_widgets = True
    field_label_classes = 'form-label-bold'

    email_declare = forms.BooleanField(label='This information is correct',
                                       widget=custom_field_widgets.CustomCheckboxInput)
    email_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)
    mobile_phone_number_declare = forms.BooleanField(label='This information is correct',
                                                     widget=custom_field_widgets.CustomCheckboxInput)
    mobile_phone_number_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)
    alternative_phone_number_declare = forms.BooleanField(label='This information is correct',
                                                          widget=custom_field_widgets.CustomCheckboxInput)
    alternative_phone_number_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)
    knowledge_based_question_declare = forms.BooleanField(label='This information is correct',
                                                          widget=custom_field_widgets.CustomCheckboxInput)
    knowledge_based_question_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)
    knowledge_based_answer_declare = forms.BooleanField(label='This information is correct',
                                                        widget=custom_field_widgets.CustomCheckboxInput)
    knowledge_based_answer_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    checkboxes = [(email_declare, 'email'), (mobile_phone_number_declare, 'mobile_phone_number'),
                  (alternative_phone_number_declare, 'alternative_phone_number'),
                  (knowledge_based_question_declare, 'knowledge_based_question'),
                  (knowledge_based_answer_declare, 'knowledge_based_answer')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'},)


class PersonalDetailsForm(GOVUKForm):
    # customisations:
    auto_replace_widgets = True

    field_label_classes = 'form-label-bold'
    name_declare = forms.BooleanField(label='This information is correct',
                                      widget=custom_field_widgets.CustomCheckboxInput)
    name_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    date_of_birth_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput)
    date_of_birth_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    home_address_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput)
    home_address_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    childcare_location_declare = forms.BooleanField(label='This information is correct',
                                                    widget=custom_field_widgets.CustomCheckboxInput)
    childcare_location_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    checkboxes = [(name_declare, 'name'), (date_of_birth_declare, 'date_of_birth'),
                  (home_address_declare, 'home_address'), (childcare_location_declare, 'childcare_location')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'},)


class FirstAidTrainingForm(GOVUKForm):
    # customisations:
    auto_replace_widgets = True

    training_organisation_declare = forms.BooleanField(label='This information is correct',
                                                       widget=custom_field_widgets.CustomCheckboxInput)
    training_organisation_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    title_of_first_aid_course_declare = forms.BooleanField(label='This information is correct',
                                                           widget=custom_field_widgets.CustomCheckboxInput)
    title_of_first_aid_course_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    date_of_certificate_declare = forms.BooleanField(label='This information is correct',
                                                     widget=custom_field_widgets.CustomCheckboxInput)
    date_of_certificate_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    checkboxes = [(training_organisation_declare, 'training_organisation'),
                  (title_of_first_aid_course_declare, 'title_of_first_aid_course'),
                  (date_of_certificate_declare, 'date_of_certificate')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'},)


class DBSCheckForm(GOVUKForm):
    # customisations:
    auto_replace_widgets = True

    dbs_certificate_number_declare = forms.BooleanField(label='This information is correct',
                                                        widget=custom_field_widgets.CustomCheckboxInput)
    dbs_certificate_number_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)
    dbs_submission_consent_declare = forms.BooleanField(label='This information is correct',
                                                        widget=custom_field_widgets.CustomCheckboxInput)
    dbs_submission_consent_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)
    cautions_or_convictions_declare = forms.BooleanField(label='This information is correct',
                                                         widget=custom_field_widgets.CustomCheckboxInput)
    cautions_or_convictions_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    checkboxes = [(dbs_certificate_number_declare, 'dbs_certificate_number'),
                  (dbs_submission_consent_declare, 'dbs_submission_consent'),
                  (cautions_or_convictions_declare, 'cautions_or_convictions')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'},)


class HealthForm(GOVUKForm):
    # customisations:
    auto_replace_widgets = True

    health_submission_consent_declare = forms.BooleanField(label='This information is correct',
                                                           widget=custom_field_widgets.CustomCheckboxInput)
    health_submission_consent_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    checkboxes = [(health_submission_consent_declare, 'health_submission_consent')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'},)


class ReferencesForm(GOVUKForm):
    # customisations:
    auto_replace_widgets = True

    full_name_declare = forms.BooleanField(label='This information is correct',
                                           widget=custom_field_widgets.CustomCheckboxInput)
    full_name_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    how_they_know_you_declare = forms.BooleanField(label='This information is correct',
                                                   widget=custom_field_widgets.CustomCheckboxInput)
    how_they_know_you_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    known_for_declare = forms.BooleanField(label='This information is correct',
                                           widget=custom_field_widgets.CustomCheckboxInput)
    known_for_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    address_declare = forms.BooleanField(label='This information is correct',
                                         widget=custom_field_widgets.CustomCheckboxInput)
    address_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    phone_number_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput)
    phone_number_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    email_address_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput)
    email_address_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    checkboxes = [(full_name_declare, 'full_name'), (how_they_know_you_declare, 'how_they_know_you'),
                  (known_for_declare, 'known_for'), (address_declare, 'address'),
                  (phone_number_declare, 'phone_number'), (email_address_declare, 'email_address')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'},)


class ReferencesForm2(GOVUKForm):
    # customisations:
    auto_replace_widgets = True

    full_name_declare = forms.BooleanField(label='This information is correct',
                                           widget=custom_field_widgets.CustomCheckboxInput)
    full_name_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    how_they_know_you_declare = forms.BooleanField(label='This information is correct',
                                                   widget=custom_field_widgets.CustomCheckboxInput)
    how_they_know_you_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    known_for_declare = forms.BooleanField(label='This information is correct',
                                           widget=custom_field_widgets.CustomCheckboxInput)
    known_for_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    address_declare = forms.BooleanField(label='This information is correct',
                                         widget=custom_field_widgets.CustomCheckboxInput)
    address_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    phone_number_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput)
    phone_number_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    email_address_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput)
    email_address_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    checkboxes = [(full_name_declare, 'full_name2'),
                  (how_they_know_you_declare, 'how_they_know_you2'),
                  (known_for_declare, 'known_for2'), (address_declare, 'address2'),
                  (phone_number_declare, 'phone_number2'),
                  (email_address_declare, 'email_address2')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )


class AdultInYourHomeForm(GOVUKForm):

    full_name_declare = forms.BooleanField(label='This information is correct',
                                           widget=custom_field_widgets.CustomCheckboxInput)
    full_name_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    date_of_birth_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput)
    date_of_birth_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    relationship_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput)
    relationship_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    dbs_certificate_declare = forms.BooleanField(label='This information is correct',
                                                 widget=custom_field_widgets.CustomCheckboxInput)
    dbs_certificate_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    permission_for_checks_declare = forms.BooleanField(label='This information is correct',
                                                       widget=custom_field_widgets.CustomCheckboxInput)
    permission_for_checks_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    checkboxes = [(full_name_declare, 'full_name'),
                  (date_of_birth_declare, 'date_of_birth'),
                  (relationship_declare, 'relationship_declare'),
                  (dbs_certificate_declare, 'dbs_certificate'),
                  (permission_for_checks_declare, 'permission_for_checks')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )


class ChildInYourHomeForm(GOVUKForm):
    full_name_declare = forms.BooleanField(label='This information is correct',
                                           widget=custom_field_widgets.CustomCheckboxInput)
    full_name_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    date_of_birth_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput)
    date_of_birth_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    relationship_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput)
    relationship_comments = forms.CharField(label='Enter your reasoning here', widget=forms.Textarea)

    checkboxes = [(full_name_declare, 'full_name'),
                  (date_of_birth_declare, 'date_of_birth'),
                  (relationship_declare, 'relationship_declare')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )

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

