"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- forms.py --
@author: Informed Solutions
"""

import uuid

import re
from django.conf import settings
from django import forms
from django.forms import ModelForm
from govuk_forms.forms import GOVUKForm
from govuk_forms.widgets import InlineRadioSelect, NumberInput, Select

from arc_application.models import OtherPersonPreviousRegistrationDetails, ArcComments
from ...widgets.ConditionalPostChoiceWidget import ConditionalPostInlineRadioSelect
from ... import custom_field_widgets
from arc_application.models import Arc as ArcReview, PreviousAddress, PreviousName
from arc_application.models import Arc as ArcReview, PreviousRegistrationDetails
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
                                      widget=custom_field_widgets.CustomCheckboxInput, required=False)
    name_comments = forms.CharField(label='Your name', help_text='(Tip: be clear and concise)',
                                    widget=custom_field_widgets.Textarea,
                                    required=False, max_length=250)

    date_of_birth_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput, required=False)
    date_of_birth_comments = forms.CharField(label='Your date of birth', help_text='(Tip: be clear and concise)',
                                             widget=custom_field_widgets.Textarea,
                                             required=False, max_length=250)

    home_address_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput, required=False)
    home_address_comments = forms.CharField(label='Home address', help_text='(Tip: be clear and concise)',
                                            widget=custom_field_widgets.Textarea,
                                            required=False, max_length=250)

    childcare_address_declare = forms.BooleanField(label='This information is correct',
                                                   widget=custom_field_widgets.CustomCheckboxInput, required=False)
    childcare_address_comments = forms.CharField(label='Childcare address', help_text='(Tip: be clear and concise)',
                                                 widget=custom_field_widgets.Textarea, required=False, max_length=250)

    working_in_other_childminder_home_declare = forms.BooleanField(label='This information is correct',
                                                                   widget=custom_field_widgets.CustomCheckboxInput,
                                                                   required=False)
    working_in_other_childminder_home_comments = forms.CharField(label="Is this another childminder's home?",
                                                                 help_text='(Tip: be clear and concise)',
                                                                 widget=custom_field_widgets.Textarea, required=False,
                                                                 max_length=250)
    own_children_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput,
                                              required=False)
    own_children_comments = forms.CharField(label="Is this another childminder's home?",
                                            help_text='(Tip: be clear and concise)',
                                            widget=custom_field_widgets.Textarea, required=False,
                                            max_length=250)

    checkboxes = [(name_declare, 'name'), (date_of_birth_declare, 'date_of_birth'),
                  (home_address_declare, 'home_address'), (childcare_address_declare, 'childcare_address'),
                  (working_in_other_childminder_home_declare, 'working_in_other_childminder_home'),
                  (own_children_declare, 'own_children')]

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
                                                                 widget=custom_field_widgets.CustomCheckboxInput,
                                                                 required=False)
    first_aid_training_organisation_comments = forms.CharField(label='Training organisation',
                                                               help_text='(Tip: be clear and concise)',
                                                               widget=custom_field_widgets.Textarea, required=False,
                                                               max_length=250)

    title_of_training_course_declare = forms.BooleanField(label='This information is correct',
                                                          widget=custom_field_widgets.CustomCheckboxInput,
                                                          required=False)
    title_of_training_course_comments = forms.CharField(label='Title of first aid course',
                                                        help_text='(Tip: be clear and concise)',
                                                        widget=custom_field_widgets.Textarea, required=False,
                                                        max_length=250)

    course_date_declare = forms.BooleanField(label='This information is correct',
                                             widget=custom_field_widgets.CustomCheckboxInput, required=False)
    course_date_comments = forms.CharField(label='Date of certificate', help_text='(Tip: be clear and concise)',
                                           widget=custom_field_widgets.Textarea, required=False, max_length=250)

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
                                                  widget=custom_field_widgets.CustomCheckboxInput,
                                                  required=False)
    eyfs_course_name_comments = forms.CharField(label='Title of training course',
                                                help_text='(Tip: be clear and concise)',
                                                widget=custom_field_widgets.Textarea, required=False, max_length=250)

    eyfs_course_date_declare = forms.BooleanField(label='This information is correct',
                                                  widget=custom_field_widgets.CustomCheckboxInput, required=False)
    eyfs_course_date_comments = forms.CharField(label='Date of training course',
                                                help_text='(Tip: be clear and concise)',
                                                widget=custom_field_widgets.Textarea, required=False, max_length=250)

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
                                                    widget=custom_field_widgets.CustomCheckboxInput, required=False)
    childcare_training_comments = forms.CharField(label='Type of childcare training',
                                                  help_text='(Tip: be clear and concise)',
                                                  widget=custom_field_widgets.Textarea, required=False, max_length=250)

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

    dbs_certificate_number_declare = forms.BooleanField(label='This information is correct',
                                                        widget=custom_field_widgets.CustomCheckboxInput, required=False)
    dbs_certificate_number_comments = forms.CharField(label='DBS certificate number',
                                                      help_text='(Tip: be clear and concise)',
                                                      widget=custom_field_widgets.Textarea, required=False,
                                                      max_length=250)
    cautions_convictions_declare = forms.BooleanField(label='This information is correct',
                                                      widget=custom_field_widgets.CustomCheckboxInput,
                                                      required=False)
    cautions_convictions_comments = forms.CharField(label='Do you have any cautions or convictions?',
                                                    help_text='(Tip: be clear and concise)',
                                                    widget=custom_field_widgets.Textarea, required=False,
                                                    max_length=250)
    lived_abroad_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput, required=False)
    lived_abroad_comments = forms.CharField(label='Have you lived outside of the UK in the last 5 years?',
                                            help_text='(Tip: be clear and concise)',
                                            widget=custom_field_widgets.Textarea, required=False,
                                            max_length=250)
    military_base_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput, required=False)
    military_base_comments = forms.CharField(
        label='Have you lived or worked on a British military base in the last 5 years?',
        help_text='(Tip: be clear and concise)',
        widget=custom_field_widgets.Textarea, required=False,
        max_length=250)
    capita_declare = forms.BooleanField(label='This information is correct',
                                        widget=custom_field_widgets.CustomCheckboxInput, required=False)
    capita_comments = forms.CharField(label='Do you have an Ofsted DBS Check?',
                                      help_text='(Tip: be clear and concise)',
                                      widget=custom_field_widgets.Textarea, required=False,
                                      max_length=250)
    on_update_declare = forms.BooleanField(label='This information is correct',
                                           widget=custom_field_widgets.CustomCheckboxInput, required=False)
    on_update_comments = forms.CharField(label='Are you on the DBS update service?',
                                         help_text='(Tip: be clear and concise)',
                                         widget=custom_field_widgets.Textarea, required=False,
                                         max_length=250)

    checkboxes = [(dbs_certificate_number_declare, 'dbs_certificate_number'),
                  (cautions_convictions_declare, 'cautions_convictions'),
                  (lived_abroad_declare, 'lived_abroad'),
                  (military_base_declare, 'military_base'),
                  (capita_declare, 'capita'),
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
                                                           widget=custom_field_widgets.CustomCheckboxInput,
                                                           required=False)
    health_submission_consent_comments = forms.CharField(label='Enter your reasoning',
                                                         help_text='(Tip: be clear and concise)',
                                                         widget=custom_field_widgets.Textarea, required=False,
                                                         max_length=250)

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
    error_summary_template_name = 'standard-error-summary.html'
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
                                           widget=custom_field_widgets.CustomCheckboxInput, required=False)
    full_name_comments = forms.CharField(label='Full name', help_text='(Tip: be clear and concise)',
                                         widget=custom_field_widgets.Textarea,
                                         required=False, max_length=250)

    relationship_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput, required=False)
    relationship_comments = forms.CharField(label='How they know you', help_text='(Tip: be clear and concise)',
                                            widget=custom_field_widgets.Textarea, required=False, max_length=250)

    time_known_declare = forms.BooleanField(label='This information is correct',
                                            widget=custom_field_widgets.CustomCheckboxInput, required=False)
    time_known_comments = forms.CharField(label='Known for', help_text='(Tip: be clear and concise)',
                                          widget=custom_field_widgets.Textarea,
                                          required=False, max_length=250)

    address_declare = forms.BooleanField(label='This information is correct',
                                         widget=custom_field_widgets.CustomCheckboxInput, required=False)
    address_comments = forms.CharField(label='Address', help_text='(Tip: be clear and concise)',
                                       widget=custom_field_widgets.Textarea,
                                       required=False, max_length=250)

    phone_number_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput, required=False)
    phone_number_comments = forms.CharField(label='Phone number', help_text='(Tip: be clear and concise)',
                                            widget=custom_field_widgets.Textarea,
                                            required=False, max_length=250)

    email_address_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput, required=False)
    email_address_comments = forms.CharField(label='Email address', help_text='(Tip: be clear and concise)',
                                             widget=custom_field_widgets.Textarea,
                                             required=False, max_length=250)

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
                                           widget=custom_field_widgets.CustomCheckboxInput, required=False)
    full_name_comments = forms.CharField(label='Full name', help_text='(Tip: be clear and concise)',
                                         widget=custom_field_widgets.Textarea,
                                         required=False, max_length=250)

    relationship_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput, required=False)
    relationship_comments = forms.CharField(label='How they know you', help_text='(Tip: be clear and concise)',
                                            widget=custom_field_widgets.Textarea, required=False, max_length=250)

    time_known_declare = forms.BooleanField(label='This information is correct',
                                            widget=custom_field_widgets.CustomCheckboxInput, required=False)
    time_known_comments = forms.CharField(label='Known for', help_text='(Tip: be clear and concise)',
                                          widget=custom_field_widgets.Textarea,
                                          required=False, max_length=250)

    address_declare = forms.BooleanField(label='This information is correct',
                                         widget=custom_field_widgets.CustomCheckboxInput, required=False)
    address_comments = forms.CharField(label='Address', help_text='(Tip: be clear and concise)',
                                       widget=custom_field_widgets.Textarea,
                                       required=False, max_length=250)

    phone_number_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput, required=False)
    phone_number_comments = forms.CharField(label='Phone number', help_text='(Tip: be clear and concise)',
                                            widget=custom_field_widgets.Textarea,
                                            required=False, max_length=250)

    email_address_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput, required=False)
    email_address_comments = forms.CharField(label='Email address', help_text='(Tip: be clear and concise)',
                                             widget=custom_field_widgets.Textarea,
                                             required=False, max_length=250)

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
                                                widget=custom_field_widgets.CustomCheckboxInput, required=False)
    adults_in_home_comments = forms.CharField(label='Do you live with anyone who is 16 or over?',
                                              help_text='(Tip: be clear and concise)',
                                              widget=custom_field_widgets.Textarea,
                                              required=False, max_length=250)
    children_in_home_declare = forms.BooleanField(label='This information is correct',
                                                  widget=custom_field_widgets.CustomCheckboxInput, required=False)
    children_in_home_comments = forms.CharField(label='Do you live with any children?',
                                                help_text='(Tip: be clear and concise)',
                                                widget=custom_field_widgets.Textarea,
                                                required=False, max_length=250)

    own_children_not_in_the_home_declare = forms.BooleanField(label='This information is correct',
                                                              widget=custom_field_widgets.CustomCheckboxInput,
                                                              required=False)
    own_children_not_in_the_home_comments = forms.CharField(label='Do you live with any children?',
                                                            help_text='(Tip: be clear and concise)',
                                                            widget=custom_field_widgets.Textarea,
                                                            required=False, max_length=250)

    checkboxes = [(adults_in_home_declare, 'adults_in_home'),
                  (children_in_home_declare, 'children_in_home'),
                  (own_children_not_in_the_home_declare, 'own_children_not_in_the_home'), ]

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

    health_check_status_declare = forms.BooleanField(label='This information is correct',
                                                     widget=custom_field_widgets.CustomCheckboxInput, required=False)
    health_check_status_comments = forms.CharField(label='Health check status',
                                                   help_text='(Tip: be clear and concise)',
                                                   widget=custom_field_widgets.Textarea,
                                                   required=False, max_length=250)

    full_name_declare = forms.BooleanField(label='This information is correct',
                                           widget=custom_field_widgets.CustomCheckboxInput, required=False)
    full_name_comments = forms.CharField(label='Name', help_text='(Tip: be clear and concise)',
                                         widget=custom_field_widgets.Textarea,
                                         required=False, max_length=250)

    date_of_birth_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput, required=False)
    date_of_birth_comments = forms.CharField(label='Date of birth', help_text='(Tip: be clear and concise)',
                                             widget=custom_field_widgets.Textarea,
                                             required=False, max_length=250)

    relationship_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput, required=False)
    relationship_comments = forms.CharField(label='Relationship', help_text='(Tip: be clear and concise)',
                                            widget=custom_field_widgets.Textarea,
                                            required=False, max_length=250)

    dbs_certificate_number_declare = forms.BooleanField(label='This information is correct',
                                                        widget=custom_field_widgets.CustomCheckboxInput, required=False)
    dbs_certificate_number_comments = forms.CharField(label='DBS certificate number',
                                                      help_text='(Tip: be clear and concise)',
                                                      widget=custom_field_widgets.Textarea,
                                                      required=False, max_length=250)

    lived_abroad_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput, required=False)
    lived_abroad_comments = forms.CharField(label='DBS certificate number',
                                            help_text='(Tip: be clear and concise)',
                                            widget=custom_field_widgets.Textarea,
                                            required=False, max_length=250)

    military_base_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput, required=False)
    military_base_comments = forms.CharField(label='DBS certificate number',
                                             help_text='(Tip: be clear and concise)',
                                             widget=custom_field_widgets.Textarea,
                                             required=False, max_length=250)

    capita_declare = forms.BooleanField(label='This information is correct',
                                        widget=custom_field_widgets.CustomCheckboxInput, required=False)
    capita_comments = forms.CharField(label='DBS certificate number',
                                      help_text='(Tip: be clear and concise)',
                                      widget=custom_field_widgets.Textarea,
                                      required=False, max_length=250)

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
            ((self.fields['dbs_certificate_number_declare']), 'dbs_certificate_number' + id_value),
            ((self.fields['lived_abroad_declare']), 'lived_abroad' + id_value),
            ((self.fields['military_base_declare']), 'military_base' + id_value),
            ((self.fields['capita_declare']), 'capita' + id_value),
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
        health_check_status_declare = self.cleaned_data['health_check_status_declare']
        health_check_status_comments = self.cleaned_data['health_check_status_comments']

        # Only check if a comment has been entered if the field has been flagged
        if health_check_status_declare is True:
            if health_check_status_comments == '':
                raise forms.ValidationError('You must give reasons')

        return health_check_status_comments

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

    def clean_lived_abroad_comments(self):
        """
        DBS certificate number comments validation
        :return: string
        """
        lived_abroad_declare = self.cleaned_data['lived_abroad_declare']
        lived_abroad_comments = self.cleaned_data['lived_abroad_comments']

        # Only check if a comment has been entered if the field has been flagged
        if lived_abroad_declare is True:
            if lived_abroad_comments == '':
                raise forms.ValidationError('You must give reasons')

        return lived_abroad_comments

    def clean_military_base_comments(self):
        """
        DBS certificate number comments validation
        :return: string
        """
        lived_abroad_declare = self.cleaned_data['military_base_declare']
        military_base_comments = self.cleaned_data['military_base_comments']

        # Only check if a comment has been entered if the field has been flagged
        if lived_abroad_declare is True:
            if military_base_comments == '':
                raise forms.ValidationError('You must give reasons')

        return military_base_comments


class YourChildrenForm(GOVUKForm):
    """
    Form for handling user responses where they have been asked which of their children reside with them
    """

    children_living_with_you_declare = forms.BooleanField(label='This information is correct',
                                                          widget=custom_field_widgets.CustomCheckboxInput,
                                                          required=False)
    children_living_with_you_comments = forms.CharField(label='Which of your children live with you?',
                                                        help_text='(Tip: be clear and concise)',
                                                        widget=custom_field_widgets.Textarea,
                                                        required=False, max_length=250)
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
                                         widget=custom_field_widgets.CustomCheckboxInput, required=False)
    address_comments = forms.CharField(label='Address', help_text='(Tip: be clear and concise)',
                                       widget=custom_field_widgets.Textarea,
                                       required=False, max_length=250)

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
                                           widget=custom_field_widgets.CustomCheckboxInput, required=False)
    full_name_comments = forms.CharField(label='Name', help_text='(Tip: be clear and concise)',
                                         widget=custom_field_widgets.Textarea(attrs={'cols': '40', 'rows': '3'}),
                                         required=False, max_length=250)

    date_of_birth_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput, required=False)
    date_of_birth_comments = forms.CharField(label='Date of birth', help_text='(Tip: be clear and concise)',
                                             widget=custom_field_widgets.Textarea,
                                             required=False, max_length=250)

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
    full_name_declare = forms.BooleanField(label='This information is correct',
                                           widget=custom_field_widgets.CustomCheckboxInput, required=False)
    full_name_comments = forms.CharField(label='Name', help_text='(Tip: be clear and concise)',
                                         widget=custom_field_widgets.Textarea(attrs={'cols': '40', 'rows': '3'}),
                                         required=False, max_length=250)

    date_of_birth_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput, required=False)
    date_of_birth_comments = forms.CharField(label='Date of birth', help_text='(Tip: be clear and concise)',
                                             widget=custom_field_widgets.Textarea,
                                             required=False, max_length=250)

    relationship_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput, required=False)
    relationship_comments = forms.CharField(label='Relationship', help_text='(Tip: be clear and concise)',
                                            widget=custom_field_widgets.Textarea,
                                            required=False, max_length=250)

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
    )

    reference_search_field = forms.CharField(label='Application number', required=False)
    name_search_field = forms.CharField(label='Name', required=False)
    dob_search_field = forms.CharField(label='Date of birth', required=False, help_text='e.g. 31 03 1980')
    home_postcode_search_field = forms.CharField(label='Home postcode', required=False)
    care_location_postcode_search_field = forms.CharField(label='Work postcode', required=False)
    application_type_dropdown_search_field = forms.ChoiceField(label='Application type',
                                                               choices=choices,
                                                               required=False,
                                                               widget=Select)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Application Search form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
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


class OtherPersonPreviousNames(GOVUKForm, ModelForm):
    """
    Form for previous names of adults in home
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    error_summary_title = "There was a problem on this page"

    def __init__(self, *args, **kwargs):
        super(OtherPersonPreviousNames, self).__init__(*args, **kwargs)

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if len(first_name) > 100:
            raise forms.ValidationError('First name must be under 100 characters long')
        else:
            return first_name

    def clean_middle_names(self):
        middle_names = self.cleaned_data['middle_names']
        if len(middle_names) > 100:
            raise forms.ValidationError('Middle names must be under 100 characters long')
        else:
            return middle_names

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if len(last_name) > 100:
            raise forms.ValidationError('Last name must be under 100 characters long')
        else:
            return last_name

    class Meta:
        model = PreviousName
        fields = ['first_name', 'middle_names', 'last_name',
                  'previous_name_id', 'person_id', 'other_person_type']
        widgets = {
            'previous_name_id': forms.HiddenInput(),
            'person_id': forms.HiddenInput(),
            'other_person_type': forms.HiddenInput()
        }


class OtherPersonPreviousPostcodeEntry(GOVUKForm):
    """
    Form for previous postcode entry of adults in home
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    error_summary_title = "There was a problem on this page"

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
            raise forms.ValidationError('Please enter a valid postcode')
        return postcode


class OtherPeoplePreviousAddressLookupForm(GOVUKForm):
    """
    Form for previous address lookup for adults in home
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    error_summary_title = "There was a problem on this page"

    address = forms.ChoiceField(label='Select address', required=True,
                                error_messages={'required': 'Please select your address'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: home address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.choices = kwargs.pop('choices')
        super(OtherPeoplePreviousAddressLookupForm, self).__init__(*args, **kwargs)
        self.fields['address'].choices = self.choices


class OtherPeoplePreviousAddressManualForm(GOVUKForm):
    """
    Form for manual previous address entry for adults in home
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    error_summary_title = "There was a problem on this page"

    street_name_and_number = forms.CharField(
        label='Address line 1',
        required=True,
        error_messages={'required': 'Please enter the first line of the address'}
    )
    street_name_and_number2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(
        label='Town or city',
        required=True,
        error_messages={'required': 'Please enter the name of the town or city'}
    )
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(
        label='Postcode',
        required=True,
        error_messages={'required': 'Please enter a postcode'}
    )

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: home address form for manual entry
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        try:
            self.address_id = kwargs.pop('id')
        except:
            self.address_id = None

        super(OtherPeoplePreviousAddressManualForm, self).__init__(*args, **kwargs)
        if PreviousAddress.objects.filter(previous_name_id=self.address_id).count() > 0:
            previous_address = PreviousAddress.objects.get(previous_name_id=self.address_id)
            self.fields['street_name_and_number'].initial = previous_address.street_line1
            self.fields['street_name_and_number2'].initial = previous_address.street_line2
            self.fields['town'].initial = previous_address.town
            self.fields['county'].initial = previous_address.county
            self.fields['postcode'].initial = previous_address.postcode
            self.pk = previous_address.previous_name_id
            self.field_list = ['street_name_and_number', 'street_name_and_number2', 'town', 'county', 'postcode']

        # If information was previously entered, display it on the form

    def clean_street_name_and_number(self):
        """
        Street name and number validation
        :return: string
        """
        street_name_and_number = self.cleaned_data['street_name_and_number']
        if len(street_name_and_number) > 50:
            raise forms.ValidationError('The first line of your address must be under 50 characters long')
        return street_name_and_number

    def clean_street_name_and_number2(self):
        """
        Street name and number line 2 validation
        :return: string
        """
        street_name_and_number2 = self.cleaned_data['street_name_and_number2']
        if len(street_name_and_number2) > 50:
            raise forms.ValidationError('The second line of your address must be under 50 characters long')
        return street_name_and_number2

    def clean_town(self):
        """
        Town validation
        :return: string
        """
        town = self.cleaned_data['town']
        if re.match(settings.REGEX['TOWN'], town) is None:
            raise forms.ValidationError('Please spell out the name of the town or city using letters')
        if len(town) > 50:
            raise forms.ValidationError('The name of the town or city must be under 50 characters long')
        return town

    def clean_county(self):
        """
        County validation
        :return: string
        """
        county = self.cleaned_data['county']
        if county != '':
            if re.match(settings.REGEX['COUNTY'], county) is None:
                raise forms.ValidationError('Please spell out the name of the county using letters')
            if len(county) > 50:
                raise forms.ValidationError('The name of the county must be under 50 characters long')
        return county


class PersonalDetailsPreviousNames(GOVUKForm, ModelForm):
    """
    Form for previous names
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    error_summary_title = "There was a problem on this page"

    def __init__(self, *args, **kwargs):
        super(PersonalDetailsPreviousNames, self).__init__(*args, **kwargs)

    class Meta:
        model = PreviousName
        fields = ['first_name', 'middle_names', 'last_name',
                  'previous_name_id', 'person_id', 'other_person_type']
        widgets = {
            'previous_name_id': forms.HiddenInput(),
            'person_id': forms.HiddenInput(),
            'other_person_type': forms.HiddenInput()
        }


class PersonalDetailsPreviousPostcodeEntry(GOVUKForm):
    """
    Form for previous postcode entry
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    error_summary_title = "There was a problem on this page"

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
            raise forms.ValidationError('Please enter a valid postcode')
        return postcode


class PersonalDetailsPreviousAddressLookupForm(GOVUKForm):
    """
    Form for previous address lookup
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    error_summary_title = "There was a problem on this page"

    address = forms.ChoiceField(label='Select address', required=True,
                                error_messages={'required': 'Please select your address'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: home address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.choices = kwargs.pop('choices')
        super(PersonalDetailsPreviousAddressLookupForm, self).__init__(*args, **kwargs)
        self.fields['address'].choices = self.choices


class PersonalDetailsPreviousAddressManualForm(GOVUKForm):
    """
    GOV.UK form for the Your personal details: home address page for manual entry
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    error_summary_title = "There was a problem on this page"

    street_name_and_number = forms.CharField(
        label='Address line 1',
        required=True,
        error_messages={'required': 'Please enter the first line of the address'}
    )
    street_name_and_number2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(
        label='Town or city',
        required=True,
        error_messages={'required': 'Please enter the name of the town or city'}
    )
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(
        label='Postcode',
        required=True,
        error_messages={'required': 'Please enter a postcode'}
    )

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: home address form for manual entry
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        try:
            self.address_id = kwargs.pop('id')
        except:
            self.address_id = None

        super(PersonalDetailsPreviousAddressManualForm, self).__init__(*args, **kwargs)
        if PreviousAddress.objects.filter(previous_name_id=self.address_id).count() > 0:
            previous_address = PreviousAddress.objects.get(previous_name_id=self.address_id)
            self.fields['street_name_and_number'].initial = previous_address.street_line1
            self.fields['street_name_and_number2'].initial = previous_address.street_line2
            self.fields['town'].initial = previous_address.town
            self.fields['county'].initial = previous_address.county
            self.fields['postcode'].initial = previous_address.postcode
            self.pk = previous_address.previous_name_id
            self.field_list = ['street_name_and_number', 'street_name_and_number2', 'town', 'county', 'postcode']

        # If information was previously entered, display it on the form

    def clean_street_name_and_number(self):
        """
        Street name and number validation
        :return: string
        """
        street_name_and_number = self.cleaned_data['street_name_and_number']
        if len(street_name_and_number) > 50:
            raise forms.ValidationError('The first line of your address must be under 50 characters long')
        return street_name_and_number

    def clean_street_name_and_number2(self):
        """
        Street name and number line 2 validation
        :return: string
        """
        street_name_and_number2 = self.cleaned_data['street_name_and_number2']
        if len(street_name_and_number2) > 50:
            raise forms.ValidationError('The second line of your address must be under 50 characters long')
        return street_name_and_number2

    def clean_town(self):
        """
        Town validation
        :return: string
        """
        town = self.cleaned_data['town']
        if re.match(settings.REGEX['TOWN'], town) is None:
            raise forms.ValidationError('Please spell out the name of the town or city using letters')
        if len(town) > 50:
            raise forms.ValidationError('The name of the town or city must be under 50 characters long')
        return town

    def clean_county(self):
        """
        County validation
        :return: string
        """
        county = self.cleaned_data['county']
        if county != '':
            if re.match(settings.REGEX['COUNTY'], county) is None:
                raise forms.ValidationError('Please spell out the name of the county using letters')
            if len(county) > 50:
                raise forms.ValidationError('The name of the county must be under 50 characters long')
        return county


class OtherPersonPreviousRegistrationDetailsForm(GOVUKForm):
    """
    GOV.UK form for adding details of previous registration.
    """
    error_summary_template_name = 'standard-error-summary.html'
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
                                              widget=ConditionalPostInlineRadioSelect, required=True,
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
