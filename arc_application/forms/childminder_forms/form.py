"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- forms.py --
@author: Informed Solutions
"""

import re
import uuid

from django import forms
from django.conf import settings
from django.forms import ModelForm
from govuk_forms.forms import GOVUKForm
from govuk_forms.widgets import InlineRadioSelect, NumberInput, Select

from ... import widgets
from ...models import Arc as ArcReview, PreviousRegistrationDetails
from ...models import OtherPersonPreviousRegistrationDetails
from ...models import PreviousAddress, PreviousName
from ...review_util import populate_initial_values, get_non_db_field_arc_comment


class CheckBox(GOVUKForm):
    pass


class PersonalDetailsForm(GOVUKForm):
    """
    Comments form for the Your personal details review page
    """
    # customisations:
    auto_replace_widgets = True

    field_label_classes = 'form-label-bold'
    name_declare = forms.BooleanField(label='This information is correct',
                                      widget=widgets.CustomCheckboxInput, required=False)
    name_comments = forms.CharField(label='Your name', help_text='(Tip: be clear and concise)',
                                    widget=widgets.Textarea,
                                    required=False, max_length=500)

    date_of_birth_declare = forms.BooleanField(label='This information is correct',
                                               widget=widgets.CustomCheckboxInput, required=False)
    date_of_birth_comments = forms.CharField(label='Your date of birth', help_text='(Tip: be clear and concise)',
                                             widget=widgets.Textarea,
                                             required=False, max_length=500)

    home_address_declare = forms.BooleanField(label='This information is correct',
                                              widget=widgets.CustomCheckboxInput, required=False)
    home_address_comments = forms.CharField(label='Home address', help_text='(Tip: be clear and concise)',
                                            widget=widgets.Textarea,
                                            required=False, max_length=500)

    childcare_address_declare = forms.BooleanField(label='This information is correct',
                                                   widget=widgets.CustomCheckboxInput, required=False)
    childcare_address_comments = forms.CharField(label='Childcare address', help_text='(Tip: be clear and concise)',
                                                 widget=widgets.Textarea, required=False, max_length=500)

    working_in_other_childminder_home_declare = forms.BooleanField(label='This information is correct',
                                                                   widget=widgets.CustomCheckboxInput,
                                                                   required=False)
    working_in_other_childminder_home_comments = forms.CharField(label="Is this another childminder's home?",
                                                                 help_text='(Tip: be clear and concise)',
                                                                 widget=widgets.Textarea, required=False,
                                                                 max_length=500)
    own_children_declare = forms.BooleanField(label='This information is correct',
                                              widget=widgets.CustomCheckboxInput,
                                              required=False)
    own_children_comments = forms.CharField(label="Known to council social services?",
                                            help_text='(Tip: be clear and concise)',
                                            widget=widgets.Textarea, required=False,
                                            max_length=500)
    reasons_known_to_social_services_declare = forms.BooleanField(label='This information is correct',
                                                                  widget=widgets.CustomCheckboxInput,
                                                                  required=False)
    reasons_known_to_social_services_comments = forms.CharField(label="Tell us why",
                                                                help_text='(Tip: be clear and concise)',
                                                                widget=widgets.Textarea, required=False,
                                                                max_length=500)

    checkboxes = [(name_declare, 'name'), (date_of_birth_declare, 'date_of_birth'),
                  (home_address_declare, 'home_address'), (childcare_address_declare, 'childcare_address'),
                  (working_in_other_childminder_home_declare, 'working_in_other_childminder_home'),
                  (own_children_declare, 'own_children'),
                  (reasons_known_to_social_services_declare, 'reasons_known_to_social_services')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )

    def __init__(self, *args, **kwargs):
        self.table_keys = kwargs.pop('table_keys')
        super(PersonalDetailsForm, self).__init__(*args, **kwargs)
        populate_initial_values(self)

    def clean_name_comments(self):
        """
        Name comments validation
        :return: string
        """
        name_declare = self.cleaned_data['name_declare']
        name_comments = self.cleaned_data['name_comments']

        # Only check if a comment has been entered if the field has been flagged
        if name_declare is True:
            if name_comments == '':
                raise forms.ValidationError('You must give reasons')

        return name_comments

    def clean_date_of_birth_comments(self):
        """
        Date of birth comments validation
        :return: string
        """
        date_of_birth_declare = self.cleaned_data['date_of_birth_declare']
        date_of_birth_comments = self.cleaned_data['date_of_birth_comments']

        # Only check if a comment has been entered if the field has been flagged
        if date_of_birth_declare is True:
            if date_of_birth_comments == '':
                raise forms.ValidationError('You must give reasons')

        return date_of_birth_comments

    def clean_home_address_comments(self):
        """
        Home address comments validation
        :return: string
        """
        home_address_declare = self.cleaned_data['home_address_declare']
        home_address_comments = self.cleaned_data['home_address_comments']

        # Only check if a comment has been entered if the field has been flagged
        if home_address_declare is True:
            if home_address_comments == '':
                raise forms.ValidationError('You must give reasons')

        return home_address_comments

    def clean_childcare_address_comments(self):
        """
        Childcare address comments validation
        :return: string
        """
        childcare_address_declare = self.cleaned_data['childcare_address_declare']
        childcare_address_comments = self.cleaned_data['childcare_address_comments']

        # Only check if a comment has been entered if the field has been flagged
        if childcare_address_declare is True:
            if childcare_address_comments == '':
                raise forms.ValidationError('You must give reasons')

        return childcare_address_comments

    def clean_working_in_other_childminder_home_comments(self):
        """
        Is this another children's home comments validation
        :return: string
        """
        working_in_other_childminder_home_declare = self.cleaned_data['working_in_other_childminder_home_declare']
        working_in_other_childminder_home_comments = self.cleaned_data['working_in_other_childminder_home_comments']

        # Only check if a comment has been entered if the field has been flagged
        if working_in_other_childminder_home_declare is True:
            if working_in_other_childminder_home_comments == '':
                raise forms.ValidationError('You must give reasons')

        return working_in_other_childminder_home_comments

    def clean_own_children_comments(self):
        """
        Do you have children of your own under 16 validation
        :return: string
        """
        own_children_declare = self.cleaned_data['own_children_declare']
        own_children_comments = self.cleaned_data['own_children_comments']

        # Only check if a comment has been entered if the field has been flagged
        if own_children_declare is True:
            if own_children_comments == '':
                raise forms.ValidationError('You must give reasons')

        return own_children_comments


class FirstAidTrainingForm(GOVUKForm):
    """
    Comments form for the First aid training review page
    """
    # customisations:
    auto_replace_widgets = True

    first_aid_training_organisation_declare = forms.BooleanField(label='This information is correct',
                                                                 widget=widgets.CustomCheckboxInput,
                                                                 required=False)
    first_aid_training_organisation_comments = forms.CharField(label='Training organisation',
                                                               help_text='(Tip: be clear and concise)',
                                                               widget=widgets.Textarea, required=False,
                                                               max_length=500)

    title_of_training_course_declare = forms.BooleanField(label='This information is correct',
                                                          widget=widgets.CustomCheckboxInput,
                                                          required=False)
    title_of_training_course_comments = forms.CharField(label='Title of first aid course',
                                                        help_text='(Tip: be clear and concise)',
                                                        widget=widgets.Textarea, required=False,
                                                        max_length=500)

    course_date_declare = forms.BooleanField(label='This information is correct',
                                             widget=widgets.CustomCheckboxInput, required=False)
    course_date_comments = forms.CharField(label='Date of certificate', help_text='(Tip: be clear and concise)',
                                           widget=widgets.Textarea, required=False, max_length=500)

    checkboxes = [(first_aid_training_organisation_declare, 'first_aid_training_organisation'),
                  (title_of_training_course_declare, 'title_of_training_course'),
                  (course_date_declare, 'course_date')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )

    def __init__(self, *args, **kwargs):
        self.table_keys = kwargs.pop('table_keys')
        super(FirstAidTrainingForm, self).__init__(*args, **kwargs)
        populate_initial_values(self)

    def clean_first_aid_training_organisation_comments(self):
        """
        First aid training organisation comments validation
        :return: string
        """
        first_aid_training_organisation_declare = self.cleaned_data['first_aid_training_organisation_declare']
        first_aid_training_organisation_comments = self.cleaned_data['first_aid_training_organisation_comments']

        # Only check if a comment has been entered if the field has been flagged
        if first_aid_training_organisation_declare is True:
            if first_aid_training_organisation_comments == '':
                raise forms.ValidationError('You must give reasons')

        return first_aid_training_organisation_comments

    def clean_title_of_training_course_comments(self):
        """
        Title of training course comments validation
        :return: string
        """
        title_of_training_course_declare = self.cleaned_data['title_of_training_course_declare']
        title_of_training_course_comments = self.cleaned_data['title_of_training_course_comments']

        # Only check if a comment has been entered if the field has been flagged
        if title_of_training_course_declare is True:
            if title_of_training_course_comments == '':
                raise forms.ValidationError('You must give reasons')

        return title_of_training_course_comments

    def clean_course_date_comments(self):
        """
        Course date comments validation
        :return: string
        """
        course_date_declare = self.cleaned_data['course_date_declare']
        course_date_comments = self.cleaned_data['course_date_comments']

        # Only check if a comment has been entered if the field has been flagged
        if course_date_declare is True:
            if course_date_comments == '':
                raise forms.ValidationError('You must give reasons')

        return course_date_comments


class EYFSTrainingCheckForm(GOVUKForm):
    """
    Comments form for the Childcare Training review page if the applicant requires EYFS training.
    """
    auto_replace_widgets = True

    eyfs_course_name_declare = forms.BooleanField(label='This information is correct',
                                                  widget=widgets.CustomCheckboxInput,
                                                  required=False)
    eyfs_course_name_comments = forms.CharField(label='Title of training course',
                                                help_text='(Tip: be clear and concise)',
                                                widget=widgets.Textarea, required=False, max_length=500)

    eyfs_course_date_declare = forms.BooleanField(label='This information is correct',
                                                  widget=widgets.CustomCheckboxInput, required=False)
    eyfs_course_date_comments = forms.CharField(label='Date of training course',
                                                help_text='(Tip: be clear and concise)',
                                                widget=widgets.Textarea, required=False, max_length=500)

    checkboxes = [(eyfs_course_name_declare, 'eyfs_course_name'),
                  (eyfs_course_date_declare, 'eyfs_course_date')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )

    def __init__(self, *args, **kwargs):
        self.table_keys = kwargs.pop('table_keys')
        super(EYFSTrainingCheckForm, self).__init__(*args, **kwargs)
        populate_initial_values(self)

    def clean_eyfs_course_name_comments(self):
        """
        EYFS course name comments validation
        :return: string
        """
        eyfs_course_name_declare = self.cleaned_data['eyfs_course_name_declare']
        eyfs_course_name_comments = self.cleaned_data['eyfs_course_name_comments']

        # Only check if a comment has been entered if the field has been flagged
        if eyfs_course_name_declare is True:
            if eyfs_course_name_comments == '':
                raise forms.ValidationError('You must give reasons')

        return eyfs_course_name_comments

    def clean_eyfs_course_date_comments(self):
        """
        EYFS course date comments validation
        :return: string
        """
        eyfs_course_date_declare = self.cleaned_data['eyfs_course_date_declare']
        eyfs_course_date_comments = self.cleaned_data['eyfs_course_date_comments']

        # Only check if a comment has been entered if the field has been flagged
        if eyfs_course_date_declare is True:
            if eyfs_course_date_comments == '':
                raise forms.ValidationError('You must give reasons')

        return eyfs_course_date_comments


class TypeOfChildcareTrainingCheckForm(GOVUKForm):
    """
    Comments form for the Childcare Training review page if the applicant requires adding to the chlidcare register only
    """
    auto_replace_widgets = True

    childcare_training_declare = forms.BooleanField(label='This information is correct',
                                                    widget=widgets.CustomCheckboxInput, required=False)
    childcare_training_comments = forms.CharField(label='Type of childcare training',
                                                  help_text='(Tip: be clear and concise)',
                                                  widget=widgets.Textarea, required=False, max_length=500)

    checkboxes = [(childcare_training_declare, 'childcare_training')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )

    def clean_childcare_training_comments(self):
        """
        Childcare Training comments validation.
        :return: childcare comments as string, if valid.
        """
        childcare_training_declare = self.cleaned_data['childcare_training_declare']
        childcare_training_comments = self.cleaned_data['childcare_training_comments']

        # Only check if a comment has been entered if the field has been flagged
        if childcare_training_declare:
            if childcare_training_comments == '':
                raise forms.ValidationError('You must give reasons')

        return childcare_training_comments

    def __init__(self, *args, **kwargs):
        self.table_keys = kwargs.pop('table_keys')
        super(TypeOfChildcareTrainingCheckForm, self).__init__(*args, **kwargs)
        populate_initial_values(self)

    def clean_eyfs_course_name_comments(self):
        """
        EYFS course name comments validation
        :return: string
        """
        eyfs_course_name_declare = self.cleaned_data['eyfs_course_name_declare']
        eyfs_course_name_comments = self.cleaned_data['eyfs_course_name_comments']

        # Only check if a comment has been entered if the field has been flagged
        if eyfs_course_name_declare is True:
            if eyfs_course_name_comments == '':
                raise forms.ValidationError('You must give reasons')

        return eyfs_course_name_comments

    def clean_eyfs_course_date_comments(self):
        """
        EYFS course date comments validation
        :return: string
        """
        eyfs_course_date_declare = self.cleaned_data['eyfs_course_date_declare']
        eyfs_course_date_comments = self.cleaned_data['eyfs_course_date_comments']

        # Only check if a comment has been entered if the field has been flagged
        if eyfs_course_date_declare is True:
            if eyfs_course_date_comments == '':
                raise forms.ValidationError('You must give reasons')

        return eyfs_course_date_comments


class DBSCheckForm(GOVUKForm):
    """
    Comments form for the Criminal record (DBS) check review page
    """
    # customisations:
    auto_replace_widgets = True

    lived_abroad_declare = forms.BooleanField(label='This information is correct',
                                              widget=widgets.CustomCheckboxInput, required=False)
    lived_abroad_comments = forms.CharField(label='Have you lived outside of the UK in the last 5 years?',
                                            help_text='(Tip: be clear and concise)',
                                            widget=widgets.Textarea, required=False,
                                            max_length=500)

    military_base_declare = forms.BooleanField(label='This information is correct',
                                               widget=widgets.CustomCheckboxInput, required=False)
    military_base_comments = forms.CharField(
        label='Have you lived or worked on a British military base in the last 5 years?',
        help_text='(Tip: be clear and concise)',
        widget=widgets.Textarea, required=False,
        max_length=500)

    capita_comments = forms.CharField(label='Did they get their DBS check from the Ofsted DBS application website?',
                                      help_text='(Tip: be clear and concise)',
                                      widget=widgets.Textarea, required=False,
                                      max_length=500)

    within_three_months_comments = forms.CharField(label='Is it dated within the last 3 months?',
                                                   help_text='(Tip: be clear and concise)',
                                                   widget=widgets.Textarea, required=False,
                                                   max_length=500)

    dbs_certificate_number_declare = forms.BooleanField(label='This information is correct',
                                                        widget=widgets.CustomCheckboxInput, required=False)
    dbs_certificate_number_comments = forms.CharField(label='DBS certificate number',
                                                      help_text='(Tip: be clear and concise)',
                                                      widget=widgets.Textarea, required=False,
                                                      max_length=500)

    enhanced_check_declare = forms.BooleanField(label='This information is correct',
                                                widget=widgets.CustomCheckboxInput, required=False)
    enhanced_check_comments = forms.CharField(label='Is it an enhanced DBS check for home-based childcare?',
                                              help_text='(Tip: be clear and concise)',
                                              widget=widgets.Textarea, required=False,
                                              max_length=500)

    on_update_declare = forms.BooleanField(label='This information is correct',
                                           widget=widgets.CustomCheckboxInput, required=False)
    on_update_comments = forms.CharField(label='Are you on the DBS Update Service?',
                                         help_text='(Tip: be clear and concise)',
                                         widget=widgets.Textarea, required=False,
                                         max_length=500)

    checkboxes = [
        (lived_abroad_declare, 'lived_abroad'),
        (military_base_declare, 'military_base'),
        (dbs_certificate_number_declare, 'dbs_certificate_number'),
        (enhanced_check_declare, 'enhanced_check'),
        (on_update_declare, 'on_update')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )

    def __init__(self, *args, **kwargs):
        self.table_keys = kwargs.pop('table_keys')
        super(DBSCheckForm, self).__init__(*args, **kwargs)
        populate_initial_values(self)

    def clean_dbs_certificate_number_comments(self):
        """
        DBS certificate number comments validation
        :return: string
        """
        dbs_certificate_number_declare = self.cleaned_data['dbs_certificate_number_declare']
        dbs_certificate_number_comments = self.cleaned_data['dbs_certificate_number_comments']

        # Only check if a comment has been entered if the field has been flagged
        if dbs_certificate_number_declare is True:
            if dbs_certificate_number_comments == '':
                raise forms.ValidationError('You must give reasons')

        return dbs_certificate_number_comments

    def clean_cautions_convictions_comments(self):
        """
        Cautions and convictions comments validation
        :return: string
        """
        cautions_convictions_declare = self.cleaned_data['cautions_convictions_declare']
        cautions_convictions_comments = self.cleaned_data['cautions_convictions_comments']

        # Only check if a comment has been entered if the field has been flagged
        if cautions_convictions_declare is True:
            if cautions_convictions_comments == '':
                raise forms.ValidationError('You must give reasons')

        return cautions_convictions_comments


class HealthForm(GOVUKForm):
    """
    Comments form for the Health declaration booklet review page
    """
    # customisations:
    auto_replace_widgets = True

    health_submission_consent_declare = forms.BooleanField(label='This information is correct',
                                                           widget=widgets.CustomCheckboxInput,
                                                           required=False)
    health_submission_consent_comments = forms.CharField(label='Enter your reasoning',
                                                         help_text='(Tip: be clear and concise)',
                                                         widget=widgets.Textarea, required=False,
                                                         max_length=500)

    checkboxes = [(health_submission_consent_declare, 'health_submission_consent')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )

    def __init__(self, *args, **kwargs):
        self.table_keys = kwargs.pop('table_keys')
        super(HealthForm, self).__init__(*args, **kwargs)
        populate_initial_values(self)

    def clean_health_submission_consent_comments(self):
        """
        Health submission consent comments validation
        :return: string
        """
        health_submission_consent_declare = self.cleaned_data['health_submission_consent_declare']
        health_submission_consent_comments = self.cleaned_data['health_submission_consent_comments']

        # Only check if a comment has been entered if the field has been flagged
        if health_submission_consent_declare is True:
            if health_submission_consent_comments == '':
                raise forms.ValidationError('You must give reasons')

        return health_submission_consent_comments


class PreviousRegistrationDetailsForm(GOVUKForm):
    """
    GOV.UK form for adding details of previous registration
    """
    error_summary_template_name = 'childminder_templates/standard-error-summary.html'
    error_summary_title = 'There was a problem on this page'
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    reveal_conditionally = {'previous_registration': {True: 'individual_id'}}

    choices = (
        (True, 'Yes'),
        (False, 'No')
    )

    previous_registration = forms.ChoiceField(choices=choices,
                                              label='Has the applicant previously registered with Ofsted?',
                                              widget=InlineRadioSelect, required=True,
                                              error_messages={'required': "Please select one"})
    custom_number_input = NumberInput()
    custom_number_input.input_classes = 'form-control form-control-1-4'
    individual_id = forms.IntegerField(label='Individual ID', widget=custom_number_input, required=False)
    five_years_in_UK = forms.ChoiceField(choices=choices,
                                         label='Has the applicant lived in England for more than 5 years?',
                                         widget=InlineRadioSelect, required=True,
                                         error_messages={'required': "Please select one"})

    def __init__(self, *args, **kwargs):
        self.application_id_local = kwargs.pop('id')
        super(PreviousRegistrationDetailsForm, self).__init__(*args, **kwargs)
        if PreviousRegistrationDetails.objects.filter(application_id=self.application_id_local).exists():
            previous_reg_details = PreviousRegistrationDetails.objects.get(application_id=self.application_id_local)
            self.fields['previous_registration'].initial = previous_reg_details.previous_registration
            self.fields['individual_id'].initial = previous_reg_details.individual_id
            self.fields['five_years_in_UK'].initial = previous_reg_details.five_years_in_UK

    def clean_individual_id(self):
        try:
            previous_registration = self.cleaned_data['previous_registration']
        except:
            previous_registration = None
        if previous_registration == 'True':
            individual_id = self.cleaned_data['individual_id']
        else:
            individual_id = None
        if previous_registration == 'True':
            if individual_id is None:
                raise forms.ValidationError("Please select one")
            if len(str(individual_id)) > 7:
                raise forms.ValidationError("Individual ID must be fewer than 7 digits")
        return individual_id


class ReferencesForm(GOVUKForm):
    """
    Comments form for the References review page: first reference
    """
    # customisations:
    auto_replace_widgets = True

    full_name_declare = forms.BooleanField(label='This information is correct',
                                           widget=widgets.CustomCheckboxInput, required=False)
    full_name_comments = forms.CharField(label='Full name', help_text='(Tip: be clear and concise)',
                                         widget=widgets.Textarea,
                                         required=False, max_length=500)

    relationship_declare = forms.BooleanField(label='This information is correct',
                                              widget=widgets.CustomCheckboxInput, required=False)
    relationship_comments = forms.CharField(label='How they know you', help_text='(Tip: be clear and concise)',
                                            widget=widgets.Textarea, required=False, max_length=500)

    time_known_declare = forms.BooleanField(label='This information is correct',
                                            widget=widgets.CustomCheckboxInput, required=False)
    time_known_comments = forms.CharField(label='Known for', help_text='(Tip: be clear and concise)',
                                          widget=widgets.Textarea,
                                          required=False, max_length=500)

    address_declare = forms.BooleanField(label='This information is correct',
                                         widget=widgets.CustomCheckboxInput, required=False)
    address_comments = forms.CharField(label='Address', help_text='(Tip: be clear and concise)',
                                       widget=widgets.Textarea,
                                       required=False, max_length=500)

    phone_number_declare = forms.BooleanField(label='This information is correct',
                                              widget=widgets.CustomCheckboxInput, required=False)
    phone_number_comments = forms.CharField(label='Phone number', help_text='(Tip: be clear and concise)',
                                            widget=widgets.Textarea,
                                            required=False, max_length=500)

    email_address_declare = forms.BooleanField(label='This information is correct',
                                               widget=widgets.CustomCheckboxInput, required=False)
    email_address_comments = forms.CharField(label='Email address', help_text='(Tip: be clear and concise)',
                                             widget=widgets.Textarea,
                                             required=False, max_length=500)

    checkboxes = [(full_name_declare, 'full_name'), (relationship_declare, 'relationship'),
                  (time_known_declare, 'time_known'), (address_declare, 'address'),
                  (phone_number_declare, 'phone_number'), (email_address_declare, 'email_address')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )

    def __init__(self, *args, **kwargs):
        self.table_keys = kwargs.pop('table_keys')
        super(ReferencesForm, self).__init__(*args, **kwargs)
        populate_initial_values(self)

    def clean_full_name_comments(self):
        """
        Full name comments validation
        :return: string
        """
        full_name_declare = self.cleaned_data['full_name_declare']
        full_name_comments = self.cleaned_data['full_name_comments']

        # Only check if a comment has been entered if the field has been flagged
        if full_name_declare is True:
            if full_name_comments == '':
                raise forms.ValidationError('You must give reasons')

        return full_name_comments

    def clean_relationship_comments(self):
        """
        Relationship comments validation
        :return: string
        """
        relationship_declare = self.cleaned_data['relationship_declare']
        relationship_comments = self.cleaned_data['relationship_comments']

        # Only check if a comment has been entered if the field has been flagged
        if relationship_declare is True:
            if relationship_comments == '':
                raise forms.ValidationError('You must give reasons')

        return relationship_comments

    def clean_time_known_comments(self):
        """
        Time known comments validation
        :return: string
        """
        time_known_declare = self.cleaned_data['time_known_declare']
        time_known_comments = self.cleaned_data['time_known_comments']

        # Only check if a comment has been entered if the field has been flagged
        if time_known_declare is True:
            if time_known_comments == '':
                raise forms.ValidationError('You must give reasons')

        return time_known_comments

    def clean_address_comments(self):
        """
        Address comments validation
        :return: string
        """
        address_declare = self.cleaned_data['address_declare']
        address_comments = self.cleaned_data['address_comments']

        # Only check if a comment has been entered if the field has been flagged
        if address_declare is True:
            if address_comments == '':
                raise forms.ValidationError('You must give reasons')

        return address_comments

    def clean_phone_number_comments(self):
        """
        Phone number comments validation
        :return: string
        """
        phone_number_declare = self.cleaned_data['phone_number_declare']
        phone_number_comments = self.cleaned_data['phone_number_comments']

        # Only check if a comment has been entered if the field has been flagged
        if phone_number_declare is True:
            if phone_number_comments == '':
                raise forms.ValidationError('You must give reasons')

        return phone_number_comments

    def clean_email_address_comments(self):
        """
        Email address comments validation
        :return: string
        """
        email_address_declare = self.cleaned_data['email_address_declare']
        email_address_comments = self.cleaned_data['email_address_comments']

        # Only check if a comment has been entered if the field has been flagged
        if email_address_declare is True:
            if email_address_comments == '':
                raise forms.ValidationError('You must give reasons')

        return email_address_comments


class ReferencesForm2(GOVUKForm):
    """
    Comments form for the References review page: second reference
    """
    # customisations:
    auto_replace_widgets = True

    full_name_declare = forms.BooleanField(label='This information is correct',
                                           widget=widgets.CustomCheckboxInput, required=False)
    full_name_comments = forms.CharField(label='Full name', help_text='(Tip: be clear and concise)',
                                         widget=widgets.Textarea,
                                         required=False, max_length=500)

    relationship_declare = forms.BooleanField(label='This information is correct',
                                              widget=widgets.CustomCheckboxInput, required=False)
    relationship_comments = forms.CharField(label='How they know you', help_text='(Tip: be clear and concise)',
                                            widget=widgets.Textarea, required=False, max_length=500)

    time_known_declare = forms.BooleanField(label='This information is correct',
                                            widget=widgets.CustomCheckboxInput, required=False)
    time_known_comments = forms.CharField(label='Known for', help_text='(Tip: be clear and concise)',
                                          widget=widgets.Textarea,
                                          required=False, max_length=500)

    address_declare = forms.BooleanField(label='This information is correct',
                                         widget=widgets.CustomCheckboxInput, required=False)
    address_comments = forms.CharField(label='Address', help_text='(Tip: be clear and concise)',
                                       widget=widgets.Textarea,
                                       required=False, max_length=500)

    phone_number_declare = forms.BooleanField(label='This information is correct',
                                              widget=widgets.CustomCheckboxInput, required=False)
    phone_number_comments = forms.CharField(label='Phone number', help_text='(Tip: be clear and concise)',
                                            widget=widgets.Textarea,
                                            required=False, max_length=500)

    email_address_declare = forms.BooleanField(label='This information is correct',
                                               widget=widgets.CustomCheckboxInput, required=False)
    email_address_comments = forms.CharField(label='Email address', help_text='(Tip: be clear and concise)',
                                             widget=widgets.Textarea,
                                             required=False, max_length=500)

    checkboxes = [(full_name_declare, 'full_name2'),
                  (relationship_declare, 'relationship2'),
                  (time_known_declare, 'time_known2'), (address_declare, 'address2'),
                  (phone_number_declare, 'phone_number2'),
                  (email_address_declare, 'email_address2')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )

    def __init__(self, *args, **kwargs):
        self.table_keys = kwargs.pop('table_keys')
        super(ReferencesForm2, self).__init__(*args, **kwargs)
        populate_initial_values(self)

    def clean_full_name_comments(self):
        """
        Full name comments validation
        :return: string
        """
        full_name_declare = self.cleaned_data['full_name_declare']
        full_name_comments = self.cleaned_data['full_name_comments']

        # Only check if a comment has been entered if the field has been flagged
        if full_name_declare is True:
            if full_name_comments == '':
                raise forms.ValidationError('You must give reasons')

        return full_name_comments

    def clean_relationship_comments(self):
        """
        Relationship comments validation
        :return: string
        """
        relationship_declare = self.cleaned_data['relationship_declare']
        relationship_comments = self.cleaned_data['relationship_comments']

        # Only check if a comment has been entered if the field has been flagged
        if relationship_declare is True:
            if relationship_comments == '':
                raise forms.ValidationError('You must give reasons')

        return relationship_comments

    def clean_time_known_comments(self):
        """
        Time known comments validation
        :return: string
        """
        time_known_declare = self.cleaned_data['time_known_declare']
        time_known_comments = self.cleaned_data['time_known_comments']

        # Only check if a comment has been entered if the field has been flagged
        if time_known_declare is True:
            if time_known_comments == '':
                raise forms.ValidationError('You must give reasons')

        return time_known_comments

    def clean_address_comments(self):
        """
        Address comments validation
        :return: string
        """
        address_declare = self.cleaned_data['address_declare']
        address_comments = self.cleaned_data['address_comments']

        # Only check if a comment has been entered if the field has been flagged
        if address_declare is True:
            if address_comments == '':
                raise forms.ValidationError('You must give reasons')

        return address_comments

    def clean_phone_number_comments(self):
        """
        Phone number comments validation
        :return: string
        """
        phone_number_declare = self.cleaned_data['phone_number_declare']
        phone_number_comments = self.cleaned_data['phone_number_comments']

        # Only check if a comment has been entered if the field has been flagged
        if phone_number_declare is True:
            if phone_number_comments == '':
                raise forms.ValidationError('You must give reasons')

        return phone_number_comments

    def clean_email_address_comments(self):
        """
        Email address comments validation
        :return: string
        """
        email_address_declare = self.cleaned_data['email_address_declare']
        email_address_comments = self.cleaned_data['email_address_comments']

        # Only check if a comment has been entered if the field has been flagged
        if email_address_declare is True:
            if email_address_comments == '':
                raise forms.ValidationError('You must give reasons')

        return email_address_comments


class OtherPeopleInYourHomeForm(GOVUKForm):
    """
    Comments form for the People in your home review page
    """

    auto_replace_widgets = True

    adults_in_home_declare = forms.BooleanField(label='This information is correct',
                                                widget=widgets.CustomCheckboxInput, required=False)
    adults_in_home_comments = forms.CharField(label='Do you live with anyone who is 16 or over?',
                                              help_text='(Tip: be clear and concise)',
                                              widget=widgets.Textarea,
                                              required=False, max_length=500)
    children_in_home_declare = forms.BooleanField(label='This information is correct',
                                                  widget=widgets.CustomCheckboxInput, required=False)
    children_in_home_comments = forms.CharField(label='Do you live with any children?',
                                                help_text='(Tip: be clear and concise)',
                                                widget=widgets.Textarea,
                                                required=False, max_length=500)

    known_to_social_services_pith_declare = forms.BooleanField(label='This information is correct',
                                                               widget=widgets.CustomCheckboxInput,
                                                               required=False)
    known_to_social_services_pith_comments = forms.CharField(label='Are you known to council social services '
                                                                   'in regards to your own children?',
                                                             help_text='(Tip: be clear and concise)',
                                                             widget=widgets.Textarea,
                                                             required=False, max_length=500)

    reasons_known_to_social_services_pith_declare = forms.BooleanField(label='This information is correct',
                                                                       widget=widgets.CustomCheckboxInput,
                                                                       required=False)
    reasons_known_to_social_services_pith_comments = forms.CharField(label='Tell us why',
                                                                     help_text='(Tip: be clear and concise)',
                                                                     widget=widgets.Textarea,
                                                                     required=False, max_length=500)

    checkboxes = [(adults_in_home_declare, 'adults_in_home'),
                  (children_in_home_declare, 'children_in_home'),
                  (known_to_social_services_pith_declare, 'known_to_social_services_pith'),
                  (reasons_known_to_social_services_pith_declare, 'reasons_known_to_social_services_pith')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )

    def __init__(self, *args, **kwargs):
        self.table_keys = kwargs.pop('table_keys')
        super(OtherPeopleInYourHomeForm, self).__init__(*args, **kwargs)
        populate_initial_values(self)

    def clean_adults_in_home_comments(self):
        """
        Adults in home comments validation
        :return: string
        """
        adults_in_home_declare = self.cleaned_data['adults_in_home_declare']
        adults_in_home_comments = self.cleaned_data['adults_in_home_comments']

        # Only check if a comment has been entered if the field has been flagged
        if adults_in_home_declare is True:
            if adults_in_home_comments == '':
                raise forms.ValidationError('You must give reasons')

        return adults_in_home_comments

    def clean_children_in_home_comments(self):
        """
        Children in home comments validation
        :return: string
        """
        children_in_home_declare = self.cleaned_data['children_in_home_declare']
        children_in_home_comments = self.cleaned_data['children_in_home_comments']

        # Only check if a comment has been entered if the field has been flagged
        if children_in_home_declare is True:
            if children_in_home_comments == '':
                raise forms.ValidationError('You must give reasons')

        return children_in_home_comments

    def clean_own_children_not_in_the_home_comments(self):
        """
        Children in home comments validation
        :return: string
        """
        own_children_not_in_the_home_declare = self.cleaned_data['own_children_not_in_the_home_declare']
        own_children_not_in_the_home_comments = self.cleaned_data['own_children_not_in_the_home_comments']

        # Only check if a comment has been entered if the field has been flagged
        if own_children_not_in_the_home_declare is True:
            if own_children_not_in_the_home_comments == '':
                raise forms.ValidationError('You must give reasons')

        return own_children_not_in_the_home_comments


class AdultInYourHomeForm(GOVUKForm):
    """
    Comments form for the People in your home review page: adults in home
    """
    auto_replace_widgets = True

    health_check_status_declare = forms.BooleanField(label='This information is correct',
                                                     widget=widgets.CustomCheckboxInput, required=False)
    health_check_status_comments = forms.CharField(label='Health check status',
                                                   help_text='(Tip: be clear and concise)',
                                                   widget=widgets.Textarea,
                                                   required=False, max_length=500)

    full_name_declare = forms.BooleanField(label='This information is correct',
                                           widget=widgets.CustomCheckboxInput, required=False)
    full_name_comments = forms.CharField(label='Name', help_text='(Tip: be clear and concise)',
                                         widget=widgets.Textarea,
                                         required=False, max_length=500)

    date_of_birth_declare = forms.BooleanField(label='This information is correct',
                                               widget=widgets.CustomCheckboxInput, required=False)
    date_of_birth_comments = forms.CharField(label='Date of birth', help_text='(Tip: be clear and concise)',
                                             widget=widgets.Textarea,
                                             required=False, max_length=500)

    relationship_declare = forms.BooleanField(label='This information is correct',
                                              widget=widgets.CustomCheckboxInput, required=False)
    relationship_comments = forms.CharField(label='Relationship', help_text='(Tip: be clear and concise)',
                                            widget=widgets.Textarea,
                                            required=False, max_length=500)

    email_declare = forms.BooleanField(label='This information is correct',
                                       widget=widgets.CustomCheckboxInput, required=False)
    email_comments = forms.CharField(label='Email', help_text='(Tip: be clear and concise)',
                                     widget=widgets.Textarea,
                                     required=False, max_length=250)

    PITH_same_address_declare = forms.BooleanField(label='This information is correct',
                                       widget=widgets.CustomCheckboxInput, required=False)
    PITH_same_address_comments = forms.CharField(label='Address', help_text='(Tip: be clear and concise)',
                                     widget=widgets.Textarea,
                                     required=False, max_length=500)

    lived_abroad_declare = forms.BooleanField(label='This information is correct',
                                              widget=widgets.CustomCheckboxInput, required=False)
    lived_abroad_comments = forms.CharField(label='Lived abroad in the last 5 years?',
                                            help_text='(Tip: be clear and concise)',
                                            widget=widgets.Textarea,
                                            required=False, max_length=500)

    military_base_declare = forms.BooleanField(label='This information is correct',
                                               widget=widgets.CustomCheckboxInput, required=False)
    military_base_comments = forms.CharField(label='Lived or worked on British military base in the last 5 years?',
                                             help_text='(Tip: be clear and concise)',
                                             widget=widgets.Textarea,
                                             required=False, max_length=500)

    capita_comments = forms.CharField(label='Did they get their DBS check from the Ofsted DBS application website?',
                                      help_text='(Tip: be clear and concise)',
                                      widget=widgets.Textarea, required=False,
                                      max_length=500)

    cygnum_relationship_choices = (
        (None, ''),
        ('Acting manager', 'Acting manager'),
        ('Boyfriend', 'Boyfriend'),
        ('Brother', 'Brother'),
        ('Brother in law', 'Brother in law'),
        ('Chairperson', 'Chairperson'),
        ('Childminding Assistant', 'Childminding Assistant'),
        ('CIO Member', 'CIO Member'),
        ('Co-Childminder', 'Co-Childminder'),
        ('Committee Member', 'Committee Member'),
        ('Co-Ordinator', 'Co-Ordinator'),
        ('Cousin', 'Cousin'),
        ('Daughter', 'Daughter'),
        ('Deputy Manager', 'Deputy Manager'),
        ('Director', 'Director'),
        ('Father', 'Father'),
        ('Father in Law', 'Father in Law'),
        ('Fiancé', 'Fiancé'),
        ('Foster Child', 'Foster Child'),
        ('Friend', 'Friend'),
        ('Governor', 'Governor'),
        ('Granddaughter', 'Granddaughter'),
        ('Grandson', 'Grandson'),
        ('Head Teacher', 'Head Teacher'),
        ('Home Childcarer', 'Home Childcarer'),
        ('Husband', 'Husband'),
        ('Job Share', 'Job Share'),
        ('Joint Manager', 'Joint Manager'),
        ('Lodger', 'Lodger'),
        ('Manager', 'Manager'),
        ('Managing Director', 'Managing Director'),
        ('Mother', 'Mother'),
        ('Mother in Law', 'Mother in Law'),
        ('Named Contact', 'Named Contact'),
        ('Nephew', 'Nephew'),
        ('Niece', 'Niece'),
        ('Owner', 'Owner'),
        ('Partner', 'Partner'),
        ('Person in Charge', 'Person in Charge'),
        ('Secretary', 'Secretary'),
        ('Sister', 'Sister'),
        ('Son', 'Son'),
        ('Son in Law', 'Son in Law'),
        ('Step-Daughter', 'Step-Daughter'),
        ('Step-Son', 'Step-Son'),
        ('Supervisor', 'Supervisor'),
        ('Tenant', 'Tenant'),
        ('Treasurer', 'Treasurer'),
        ('Trustee', 'Trustee'),
        ('Vice Chair', 'Vice Chair'),
        ('Wife', 'Wife'),
    )

    cygnum_relationship = forms.ChoiceField(
        label='Select (Cygnum) relationship type',
        required=True,
        error_messages={
            'required': 'You must select a relationship type for this person'
        },
        choices=cygnum_relationship_choices,
    )

    within_three_months_comments = forms.CharField(label='Is it dated within the last 3 months?',
                                                   help_text='(Tip: be clear and concise)',
                                                   widget=widgets.Textarea, required=False,
                                                   max_length=500)

    dbs_certificate_number_declare = forms.BooleanField(label='This information is correct',
                                                        widget=widgets.CustomCheckboxInput, required=False)
    dbs_certificate_number_comments = forms.CharField(label='DBS certificate number',
                                                      help_text='(Tip: be clear and concise)',
                                                      widget=widgets.Textarea,
                                                      required=False, max_length=500)

    enhanced_check_declare = forms.BooleanField(label='This information is correct',
                                                widget=widgets.CustomCheckboxInput, required=False)
    enhanced_check_comments = forms.CharField(label='Is it an enhanced DBS check for home-based childcare?',
                                              help_text='(Tip: be clear and concise)',
                                              widget=widgets.Textarea, required=False,
                                              max_length=500)

    on_update_declare = forms.BooleanField(label='This information is correct',
                                           widget=widgets.CustomCheckboxInput, required=False)
    on_update_comments = forms.CharField(label='On the DBS Update Service?',
                                         help_text='(Tip: be clear and concise)',
                                         widget=widgets.Textarea,
                                         required=False, max_length=500)

    known_to_council_comments = forms.CharField(
        label='Known to council social Services in regards to their own children?',
        help_text='(Tip: be clear and concise)',
        widget=widgets.Textarea, required=False,
        max_length=500)

    reasons_known_to_social_services_pith_comments = forms.CharField(label='Tell us why',
                                                                     help_text='(Tip: be clear and concise)',
                                                                     widget=widgets.Textarea,
                                                                     required=False, max_length=500)

    # This is the id appended to all htmls names ot make the individual form instance unique, this is given a value in
    # the init
    instance_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super(AdultInYourHomeForm, self).__init__(*args, **kwargs)
        # Create unique id value and populate the instance_id field with it
        id_value = str(uuid.uuid4())
        self.fields['instance_id'].initial = id_value
        # Make all checkbox names refer the the name with the correct instance id, making each conditional reveal unique
        checkboxes = [
            ((self.fields['health_check_status_declare']), 'health_check_status' + id_value),
            ((self.fields['full_name_declare']), 'full_name' + id_value),
            ((self.fields['date_of_birth_declare']), 'date_of_birth' + id_value),
            ((self.fields['relationship_declare']), 'relationship' + id_value),
            ((self.fields['email_declare']), 'email' + id_value),
            ((self.fields['PITH_same_address_declare']), 'PITH_same_address' + id_value),
            ((self.fields['dbs_certificate_number_declare']), 'dbs_certificate_number' + id_value),
            ((self.fields['enhanced_check_declare']), 'enhanced_check' + id_value),
            ((self.fields['on_update_declare']), 'on_update' + id_value),
            ((self.fields['lived_abroad_declare']), 'lived_abroad' + id_value),
            ((self.fields['military_base_declare']), 'military_base' + id_value),
        ]

        for box in checkboxes:
            box[0].widget.attrs.update({'data_target': box[1],
                                        'aria-controls': box[1],
                                        'aria-expanded': 'false'}, )

    def clean_health_check_status_comments(self):
        """
        Health check status comments validation
        :return: string
        """
        return self.helper_clean('health_check_status')

    def clean_full_name_comments(self):
        """
        Full name comments validation
        :return: string
        """
        return self.helper_clean('full_name')

    def clean_date_of_birth_comments(self):
        """
        Date of birth comments validation
        :return: string
        """
        return self.helper_clean('date_of_birth')

    def clean_relationship_comments(self):
        """
        Relationship comments validation
        :return: string
        """
        return self.helper_clean('relationship')

    def clean_email_comments(self):
        """
        Email comment validation
        :return: string
        """
        return self.helper_clean('email')

    def clean_address_comments(self):
        """
        Email comment validation
        :return: string
        """
        return self.helper_clean('PITH_same_address')

    def clean_dbs_certificate_number_comments(self):
        """
        DBS certificate number comments validation
        :return: string
        """
        return self.helper_clean('dbs_certificate_number')

    def clean_on_update_comments(self):
        """
        DBS holder-on-update-service comments validation
        :return: string
        """
        return self.helper_clean('on_update')

    def clean_lived_abroad_comments(self):
        """
        DBS certificate number comments validation
        :return: string
        """
        return self.helper_clean('lived_abroad')

    def clean_military_base_comments(self):
        """
        DBS certificate number comments validation
        :return: string
        """
        return self.helper_clean('military_base')

    def clean_enhanced_check_comments(self):
        """
        PITH enhanced_check comments validation
        :return: string
        """
        return self.helper_clean('enhanced_check')

    def helper_clean(self, field):
        """
        Validation helper method
        :return: string
        """
        field_declare = self.cleaned_data['{0}_declare'.format(field)]
        field_comments = self.cleaned_data['{0}_comments'.format(field)]

        # Only check if a comment has been entered if the field has been flagged
        if field_declare is True:
            if field_comments == '':
                raise forms.ValidationError('You must give reasons')

        return field_comments


class YourChildrenForm(GOVUKForm):
    """
    Form for handling user responses where they have been asked which of their children reside with them
    """

    children_living_with_you_declare = forms.BooleanField(label='This information is correct',
                                                          widget=widgets.CustomCheckboxInput,
                                                          required=False)
    children_living_with_you_comments = forms.CharField(label='Which of your children live with you?',
                                                        help_text='(Tip: be clear and concise)',
                                                        widget=widgets.Textarea,
                                                        required=False, max_length=500)

    instance_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.application_id = kwargs.pop('application_id')
        self.table_keys = kwargs.pop('table_keys')
        super(YourChildrenForm, self).__init__(*args, **kwargs)
        id_value = str(uuid.uuid4())
        self.fields['instance_id'].initial = id_value

        checkboxes = [((self.fields['children_living_with_you_declare']), 'children_living_with_you' + id_value)]

        for box in checkboxes:
            box[0].widget.attrs.update({'data_target': box[1],
                                        'aria-controls': box[1],
                                        'aria-expanded': 'false'}, )

        arc_comment = get_non_db_field_arc_comment(self.application_id, 'children_living_with_childminder_selection')

        if arc_comment is not None and arc_comment.flagged:
            self.fields['children_living_with_you_declare'].initial = True
            try:
                self.fields['children_living_with_you_comments'].initial = arc_comment.comment
            except:
                pass

    def clean_children_living_with_you_comments(self):
        """
        Full name comments validation
        :return: string
        """
        children_living_with_you_declare = self.cleaned_data['children_living_with_you_declare']
        children_living_with_you_comments = self.cleaned_data['children_living_with_you_comments']

        # Only check if a comment has been entered if the field has been flagged
        if children_living_with_you_declare is True:
            if children_living_with_you_comments == '':
                raise forms.ValidationError('You must give reasons')

        return children_living_with_you_comments


class ChildAddressForm(GOVUKForm):
    """
    Form for handling user responses where their children address have been detailed
    """

    address_declare = forms.BooleanField(label='This information is correct',
                                         widget=widgets.CustomCheckboxInput, required=False)
    address_comments = forms.CharField(label='Address', help_text='(Tip: be clear and concise)',
                                       widget=widgets.Textarea,
                                       required=False, max_length=500)

    instance_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean_address_comments(self):
        """
        Address comments validation
        :return: string
        """
        address_declare = self.cleaned_data['address_declare']
        address_comments = self.cleaned_data['address_comments']

        # Only check if a comment has been entered if the field has been flagged
        if address_declare is True:
            if address_comments == '':
                raise forms.ValidationError('You must give reasons')

        return address_comments

    def __init__(self, *args, **kwargs):
        super(ChildAddressForm, self).__init__(*args, **kwargs)
        id_value = str(uuid.uuid4())
        self.fields['instance_id'].initial = id_value

        checkboxes = [((self.fields['address_declare']), 'address' + id_value)]

        for box in checkboxes:
            box[0].widget.attrs.update({'data_target': box[1],
                                        'aria-controls': box[1],
                                        'aria-expanded': 'false'}, )

    def clean_address_comments(self):
        """
        Address comments validation
        :return: string
        """
        address_declare = self.cleaned_data['address_declare']
        address_comments = self.cleaned_data['address_comments']

        # Only check if a comment has been entered if the field has been flagged
        if address_declare is True:
            if address_comments == '':
                raise forms.ValidationError('You must give reasons')

        return address_comments


class ChildForm(GOVUKForm):
    """
    Comments form for the Your children review page
    """

    full_name_declare = forms.BooleanField(label='This information is correct',
                                           widget=widgets.CustomCheckboxInput, required=False)
    full_name_comments = forms.CharField(label='Name', help_text='(Tip: be clear and concise)',
                                         widget=widgets.Textarea(attrs={'cols': '40', 'rows': '3'}),
                                         required=False, max_length=500)

    date_of_birth_declare = forms.BooleanField(label='This information is correct',
                                               widget=widgets.CustomCheckboxInput, required=False)
    date_of_birth_comments = forms.CharField(label='Date of birth', help_text='(Tip: be clear and concise)',
                                             widget=widgets.Textarea,
                                             required=False, max_length=500)

    instance_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super(ChildForm, self).__init__(*args, **kwargs)
        id_value = str(uuid.uuid4())
        self.fields['instance_id'].initial = id_value

        checkboxes = [((self.fields['full_name_declare']), 'full_name' + id_value),
                      ((self.fields['date_of_birth_declare']), 'date_of_birth' + id_value)]

        for box in checkboxes:
            box[0].widget.attrs.update({'data_target': box[1],
                                        'aria-controls': box[1],
                                        'aria-expanded': 'false'}, )

    def clean_full_name_comments(self):
        """
        Full name comments validation
        :return: string
        """
        full_name_declare = self.cleaned_data['full_name_declare']
        full_name_comments = self.cleaned_data['full_name_comments']

        # Only check if a comment has been entered if the field has been flagged
        if full_name_declare is True:
            if full_name_comments == '':
                raise forms.ValidationError('You must give reasons')

        return full_name_comments

    def clean_date_of_birth_comments(self):
        """
        Date of birth comments validation
        :return: string
        """
        date_of_birth_declare = self.cleaned_data['date_of_birth_declare']
        date_of_birth_comments = self.cleaned_data['date_of_birth_comments']

        # Only check if a comment has been entered if the field has been flagged
        if date_of_birth_declare is True:
            if date_of_birth_comments == '':
                raise forms.ValidationError('You must give reasons')

        return date_of_birth_comments


class ChildInYourHomeForm(GOVUKForm):
    """
    Comments form for the People in your home review page: children in home
    """
    auto_replace_widgets = True

    full_name_declare = forms.BooleanField(label='This information is correct',
                                           widget=widgets.CustomCheckboxInput, required=False)
    full_name_comments = forms.CharField(label='Name', help_text='(Tip: be clear and concise)',
                                         widget=widgets.Textarea(attrs={'cols': '40', 'rows': '3'}),
                                         required=False, max_length=500)

    date_of_birth_declare = forms.BooleanField(label='This information is correct',
                                               widget=widgets.CustomCheckboxInput, required=False)
    date_of_birth_comments = forms.CharField(label='Date of birth', help_text='(Tip: be clear and concise)',
                                             widget=widgets.Textarea,
                                             required=False, max_length=500)

    relationship_declare = forms.BooleanField(label='This information is correct',
                                              widget=widgets.CustomCheckboxInput, required=False)
    relationship_comments = forms.CharField(label='Relationship', help_text='(Tip: be clear and concise)',
                                            widget=widgets.Textarea,
                                            required=False, max_length=500)

    instance_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super(ChildInYourHomeForm, self).__init__(*args, **kwargs)
        id_value = str(uuid.uuid4())
        self.fields['instance_id'].initial = id_value

        checkboxes = [((self.fields['full_name_declare']), 'full_name' + id_value),
                      ((self.fields['date_of_birth_declare']), 'date_of_birth' + id_value),
                      ((self.fields['relationship_declare']), 'relationship' + id_value)]

        for box in checkboxes:
            box[0].widget.attrs.update({'data_target': box[1],
                                        'aria-controls': box[1],
                                        'aria-expanded': 'false'}, )

    def clean_full_name_comments(self):
        """
        Full name comments validation
        :return: string
        """
        full_name_declare = self.cleaned_data['full_name_declare']
        full_name_comments = self.cleaned_data['full_name_comments']

        # Only check if a comment has been entered if the field has been flagged
        if full_name_declare is True:
            if full_name_comments == '':
                raise forms.ValidationError('You must give reasons')

        return full_name_comments

    def clean_date_of_birth_comments(self):
        """
        Date of birth comments validation
        :return: string
        """
        date_of_birth_declare = self.cleaned_data['date_of_birth_declare']
        date_of_birth_comments = self.cleaned_data['date_of_birth_comments']

        # Only check if a comment has been entered if the field has been flagged
        if date_of_birth_declare is True:
            if date_of_birth_comments == '':
                raise forms.ValidationError('You must give reasons')

        return date_of_birth_comments

    def clean_relationship_comments(self):
        """
        Relationship comments validation
        :return: string
        """
        relationship_declare = self.cleaned_data['relationship_declare']
        relationship_comments = self.cleaned_data['relationship_comments']

        # Only check if a comment has been entered if the field has been flagged
        if relationship_declare is True:
            if relationship_comments == '':
                raise forms.ValidationError('You must give reasons')

        return relationship_comments


class CommentsForm(GOVUKForm):
    """
    Form for Comments page
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


class SearchForm(GOVUKForm):
    """
    Search page form
    """
    field_label_classes = 'form-label-bold'
    field_help_classes = 'search-help-text form-hint'
    auto_replace_widgets = True
    error_summary_title = "There was a problem on this page"

    choices = (
        ('All', 'All'),
        ('Childminder', 'Childminder'),
        ('Nanny', 'Nanny'),
        ('Association', 'Association')
    )

    reference_search_field = forms.CharField(label='Application number', required=False)
    name_search_field = forms.CharField(label='Name', required=False)
    dob_search_field = forms.CharField(label='Date of birth', required=False, help_text='e.g. 31 03 1980')
    home_postcode_search_field = forms.CharField(label='Home postcode', required=False)
    care_location_postcode_search_field = forms.CharField(label='Work postcode', required=False)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Application Search form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        if settings.ENABLE_NANNIES:
            self.base_fields['application_type_dropdown_search_field'] = forms.ChoiceField(label='Application type',
                                                                                           choices=self.choices,
                                                                                           required=False,
                                                                                           widget=Select)
        super(SearchForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        Custom form cleansing override
        """
        cleaned_data = super(SearchForm, self).clean()

        name = self.cleaned_data['name_search_field']
        dob = self.cleaned_data['dob_search_field']
        home_postcode = self.cleaned_data['home_postcode_search_field']
        care_location_postcode = self.cleaned_data['care_location_postcode_search_field']
        reference = self.cleaned_data['reference_search_field']

        length_error_text = 'Please enter more than 2 characters'
        less_than_two_text_error = 'Please enter more than one character'

        if len(reference) != 0 and len(reference) < 3:
            self.add_error('reference_search_field', length_error_text)

        if len(name) != 0 and len(name) < 2:
            self.add_error('name_search_field', less_than_two_text_error)

        if len(dob) != 0 and len(dob) < 2:
            self.add_error('dob_search_field', less_than_two_text_error)

        if len(home_postcode) != 0 and len(home_postcode) < 3:
            self.add_error('home_postcode_search_field', length_error_text)

        if len(care_location_postcode) != 0 and len(care_location_postcode) < 3:
            self.add_error('care_location_postcode_search_field', length_error_text)

        if len(self.errors):
            self.error_summary_title = 'There was a problem with your search'

        return cleaned_data


class OtherPersonPreviousRegistrationDetailsForm(GOVUKForm):
    """
    GOV.UK form for adding details of previous registration.
    """
    error_summary_template_name = 'childminder_templates/standard-error-summary.html'
    error_summary_title = 'There was a problem on this page'
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    reveal_conditionally = {'previous_registration': {True: 'individual_id'}}

    choices = (
        (True, 'Yes'),
        (False, 'No'),
    )

    previous_registration = forms.ChoiceField(choices=choices,
                                              label='Has the person previously registered with Ofsted?',
                                              widget=widgets.ConditionalPostInlineRadioSelect, required=True,
                                              error_messages={'required': "Please select one"})
    custom_number_input = NumberInput()
    custom_number_input.input_classes = 'form-control form-control-1-4'
    individual_id = forms.IntegerField(label='Individual ID', widget=custom_number_input, required=False)
    five_years_in_UK = forms.ChoiceField(choices=choices,
                                         label='Has the person lived in England for more than 5 years?',
                                         widget=InlineRadioSelect, required=True,
                                         error_messages={'required': "Please select one"})

    def __init__(self, *args, **kwargs):
        self.person_id = kwargs.pop('id')
        super(OtherPersonPreviousRegistrationDetailsForm, self).__init__(*args, **kwargs)
        if OtherPersonPreviousRegistrationDetails.objects.filter(person_id=self.person_id).exists():
            previous_reg_details = OtherPersonPreviousRegistrationDetails.objects.get(person_id=self.person_id)
            self.fields['previous_registration'].initial = previous_reg_details.previous_registration
            self.fields['individual_id'].initial = previous_reg_details.individual_id
            self.fields['five_years_in_UK'].initial = previous_reg_details.five_years_in_UK

    def clean_individual_id(self):
        try:
            previous_registration = self.cleaned_data['previous_registration']
        except:
            previous_registration = None
        if previous_registration == 'True':
            individual_id = self.cleaned_data['individual_id']
        else:
            individual_id = None
        if previous_registration == 'True':
            if individual_id is None:
                raise forms.ValidationError("Please select one")
            if len(str(individual_id)) > 7:
                raise forms.ValidationError("Individual ID must be fewer than 7 digits")
        return individual_id
