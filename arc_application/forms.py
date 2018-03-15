"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- forms.py --

@author: Informed Solutions
"""

import uuid

from django import forms
from govuk_forms.forms import GOVUKForm

from . import custom_field_widgets
from .models import Arc as ArcReview
from .review_util import populate_initial_values


class CheckBox(GOVUKForm):
    pass


class LogInDetailsForm(GOVUKForm):
    """
    GOV.UK form for the Your login and contact details: email page
    """
    # customisations:
    auto_replace_widgets = True
    field_label_classes = 'form-label-bold'

    email_address_declare = forms.BooleanField(label='This information is correct',
                                       widget=custom_field_widgets.CustomCheckboxInput, required=False)
    email_address_comments = forms.CharField(label='Enter your reasoning here',
                                     widget=custom_field_widgets.Textarea(attrs={'cols': '40', 'rows': '3'}),
                                     required=False)
    mobile_number_declare = forms.BooleanField(label='This information is correct',
                                                     widget=custom_field_widgets.CustomCheckboxInput, required=False)
    mobile_number_comments = forms.CharField(label='Enter your reasoning here',
                                                   widget=custom_field_widgets.Textarea, required=False)
    add_phone_number_declare = forms.BooleanField(label='This information is correct',
                                                          widget=custom_field_widgets.CustomCheckboxInput,
                                                          required=False)
    add_phone_number_comments = forms.CharField(label='Enter your reasoning here',
                                                        widget=custom_field_widgets.Textarea, required=False)
    security_question_declare = forms.BooleanField(label='This information is correct',
                                                          widget=custom_field_widgets.CustomCheckboxInput,
                                                          required=False)
    security_question_comments = forms.CharField(label='Enter your reasoning here',
                                                        widget=custom_field_widgets.Textarea, required=False)
    security_answer_declare = forms.BooleanField(label='This information is correct',
                                                        widget=custom_field_widgets.CustomCheckboxInput, required=False)
    security_answer_comments = forms.CharField(label='Enter your reasoning here',
                                                      widget=custom_field_widgets.Textarea, required=False)

    # As this will only happen once per page, we can do this in the form itself rather than __init
    # Each checkbox must be assigned a name for the html injection
    checkboxes = [(email_address_declare, 'email'), (mobile_number_declare, 'mobile_number'),
                  (add_phone_number_declare, 'add_phone_number'),
                  (security_question_declare, 'security_question'),
                  (security_answer_declare, 'security_answer')]

    # This is where the html is added that assigns each checkbox with the correct name, so the javascript knows where
    # act
    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )

    def __init__(self, *args, **kwargs):
        self.table_keys = kwargs.pop('table_keys')
        super(LogInDetailsForm, self).__init__(*args, **kwargs)
        populate_initial_values(self)


class PersonalDetailsForm(GOVUKForm):
    """
    GOV.UK form for the Personal details page
    """
    # customisations:
    auto_replace_widgets = True

    field_label_classes = 'form-label-bold'
    name_declare = forms.BooleanField(label='This information is correct',
                                      widget=custom_field_widgets.CustomCheckboxInput, required=False)
    name_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                    required=False)

    date_of_birth_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput, required=False)
    date_of_birth_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                             required=False)

    home_address_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput, required=False)
    home_address_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                            required=False)

    childcare_location_declare = forms.BooleanField(label='This information is correct',
                                                    widget=custom_field_widgets.CustomCheckboxInput, required=False)
    childcare_location_comments = forms.CharField(label='Enter your reasoning here',
                                                  widget=custom_field_widgets.Textarea, required=False)

    checkboxes = [(name_declare, 'name'), (date_of_birth_declare, 'date_of_birth'),
                  (home_address_declare, 'home_address'), (childcare_location_declare, 'childcare_location')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )

    def __init__(self, *args, **kwargs):
        self.table_keys = kwargs.pop('table_keys')
        super(PersonalDetailsForm, self).__init__(*args, **kwargs)
        populate_initial_values(self)


class FirstAidTrainingForm(GOVUKForm):
    """
    GOV.UK form for the First Aid Training Form
    """
    # customisations:
    auto_replace_widgets = True

    first_aid_training_organisation_declare = forms.BooleanField(label='This information is correct',
                                                       widget=custom_field_widgets.CustomCheckboxInput, required=False)
    first_aid_training_organisation_comments = forms.CharField(label='Enter your reasoning here',
                                                     widget=custom_field_widgets.Textarea, required=False)

    title_of_training_course_declare = forms.BooleanField(label='This information is correct',
                                                           widget=custom_field_widgets.CustomCheckboxInput,
                                                           required=False)
    title_of_first_aid_course_comments = forms.CharField(label='Enter your reasoning here',
                                                         widget=custom_field_widgets.Textarea, required=False)

    course_date_declare = forms.BooleanField(label='This information is correct',
                                                     widget=custom_field_widgets.CustomCheckboxInput, required=False)
    course_date_comments = forms.CharField(label='Enter your reasoning here',
                                                   widget=custom_field_widgets.Textarea, required=False)

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


class DBSCheckForm(GOVUKForm):
    """
    GOV.UK form for the Your login and contact details: email page
    """
    # customisations:
    auto_replace_widgets = True

    dbs_certificate_number_declare = forms.BooleanField(label='This information is correct',
                                                        widget=custom_field_widgets.CustomCheckboxInput, required=False)
    dbs_certificate_number_comments = forms.CharField(label='Enter your reasoning here',
                                                      widget=custom_field_widgets.Textarea, required=False)
    dbs_submission_consent_declare = forms.BooleanField(label='This information is correct',
                                                        widget=custom_field_widgets.CustomCheckboxInput, required=False)
    dbs_submission_consent_comments = forms.CharField(label='Enter your reasoning here',
                                                      widget=custom_field_widgets.Textarea, required=False)
    cautions_or_convictions_declare = forms.BooleanField(label='This information is correct',
                                                         widget=custom_field_widgets.CustomCheckboxInput,
                                                         required=False)
    cautions_or_convictions_comments = forms.CharField(label='Enter your reasoning here',
                                                       widget=custom_field_widgets.Textarea, required=False)

    checkboxes = [(dbs_certificate_number_declare, 'dbs_certificate_number'),
                  (dbs_submission_consent_declare, 'dbs_submission_consent'),
                  (cautions_or_convictions_declare, 'cautions_or_convictions')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )

    def __init__(self, *args, **kwargs):
        self.table_keys = kwargs.pop('table_keys')
        super(DBSCheckForm, self).__init__(*args, **kwargs)
        populate_initial_values(self)


class HealthForm(GOVUKForm):
    """
    GOV.UK form for the Health Page
    """
    # customisations:
    auto_replace_widgets = True

    health_submission_consent_declare = forms.BooleanField(label='This information is correct',
                                                           widget=custom_field_widgets.CustomCheckboxInput,
                                                           required=False)
    health_submission_consent_comments = forms.CharField(label='Enter your reasoning here',
                                                         widget=custom_field_widgets.Textarea, required=False)

    checkboxes = [(health_submission_consent_declare, 'health_submission_consent')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )

    def __init__(self, *args, **kwargs):
        self.table_keys = kwargs.pop('table_keys')
        super(HealthForm, self).__init__(*args, **kwargs)
        populate_initial_values(self)


class ReferencesForm(GOVUKForm):
    """
    GOV.UK form for the first reference
    """
    # customisations:
    auto_replace_widgets = True

    full_name_declare = forms.BooleanField(label='This information is correct',
                                           widget=custom_field_widgets.CustomCheckboxInput, required=False)
    full_name_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                         required=False)

    relationship_declare = forms.BooleanField(label='This information is correct',
                                                   widget=custom_field_widgets.CustomCheckboxInput, required=False)
    relationship_comments = forms.CharField(label='Enter your reasoning here',
                                                 widget=custom_field_widgets.Textarea, required=False)

    time_known_declare = forms.BooleanField(label='This information is correct',
                                           widget=custom_field_widgets.CustomCheckboxInput, required=False)
    time_known_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                         required=False)

    address_declare = forms.BooleanField(label='This information is correct',
                                         widget=custom_field_widgets.CustomCheckboxInput, required=False)
    address_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                       required=False)

    phone_number_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput, required=False)
    phone_number_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                            required=False)

    email_address_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput, required=False)
    email_address_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                             required=False)

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


class ReferencesForm2(GOVUKForm):
    """
    GOV.UK form for the second reference, this can be deleted later if these are done dynamically
    """
    # customisations:
    auto_replace_widgets = True

    full_name_declare = forms.BooleanField(label='This information is correct',
                                           widget=custom_field_widgets.CustomCheckboxInput, required=False)
    full_name_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                         required=False)

    relationship_declare = forms.BooleanField(label='This information is correct',
                                                   widget=custom_field_widgets.CustomCheckboxInput, required=False)
    relationship_comments = forms.CharField(label='Enter your reasoning here',
                                                 widget=custom_field_widgets.Textarea, required=False)

    time_known_declare = forms.BooleanField(label='This information is correct',
                                           widget=custom_field_widgets.CustomCheckboxInput, required=False)
    time_known_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                         required=False)

    address_declare = forms.BooleanField(label='This information is correct',
                                         widget=custom_field_widgets.CustomCheckboxInput, required=False)
    address_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                       required=False)

    phone_number_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput, required=False)
    phone_number_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                            required=False)

    email_address_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput, required=False)
    email_address_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                             required=False)

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


class OtherPeopleInYourHomeForm(GOVUKForm):
    """
    GOV.UK form for the top part ot the other people form, that isnt rendered manually
    """

    auto_replace_widgets = True

    adults_in_home_declare = forms.BooleanField(label='This information is correct',
                                                widget=custom_field_widgets.CustomCheckboxInput, required=False)
    adults_in_home_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                              required=False)
    children_in_home_declare = forms.BooleanField(label='This information is correct',
                                                  widget=custom_field_widgets.CustomCheckboxInput, required=False)
    children_in_home_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                                required=False)

    checkboxes = [(adults_in_home_declare, 'adults_in_home'),
                  (children_in_home_declare, 'children_in_home')]

    for box in checkboxes:
        box[0].widget.attrs.update({'data_target': box[1],
                                    'aria-controls': box[1],
                                    'aria-expanded': 'false'}, )

    def __init__(self, *args, **kwargs):
        self.table_keys = kwargs.pop('table_keys')
        super(OtherPeopleInYourHomeForm, self).__init__(*args, **kwargs)
        populate_initial_values(self)


class AdultInYourHomeForm(GOVUKForm):
    """
    GOV.UK form for each adult other person in an application
    """

    full_name_declare = forms.BooleanField(label='This information is correct',
                                           widget=custom_field_widgets.CustomCheckboxInput, required=False)
    full_name_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                         required=False)

    date_of_birth_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput, required=False)
    date_of_birth_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                             required=False)

    relationship_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput, required=False)
    relationship_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                            required=False)

    dbs_certificate_number_declare = forms.BooleanField(label='This information is correct',
                                                 widget=custom_field_widgets.CustomCheckboxInput, required=False)
    dbs_certificate_number_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                               required=False)

    permission_declare = forms.BooleanField(label='This information is correct',
                                                       widget=custom_field_widgets.CustomCheckboxInput, required=False)
    permission_comments = forms.CharField(label='Enter your reasoning here',
                                                     widget=custom_field_widgets.Textarea, required=False)

    # This is the id appended to all htmls names ot make the individual form instance unique, this is given a alue in
    # the init
    instance_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super(AdultInYourHomeForm, self).__init__(*args, **kwargs)
        # Create unique id value and populate the instance_id field with it
        id_value = str(uuid.uuid4())
        self.fields['instance_id'].initial = id_value
        # print(self.fields['instance_id'].initial)
        # Make all checkbox names refer the the name with the correct instance id, making each conditional reveal unique
        checkboxes = [((self.fields['full_name_declare']), 'full_name' + id_value),
                      ((self.fields['date_of_birth_declare']), 'date_of_birth' + id_value),
                      ((self.fields['relationship_declare']), 'relationship' + id_value),
                      ((self.fields['dbs_certificate_number_declare']), 'dbs_certificate_number' + id_value),
                      ((self.fields['permission_declare']), 'permission_declare' + id_value)]

        for box in checkboxes:
            box[0].widget.attrs.update({'data_target': box[1],
                                        'aria-controls': box[1],
                                        'aria-expanded': 'false'}, )


class ChildInYourHomeForm(GOVUKForm):
    """
    GOV.UK form for each child other person in an application, see adult form for comment explanation
    """
    full_name_declare = forms.BooleanField(label='This information is correct',
                                           widget=custom_field_widgets.CustomCheckboxInput, required=False)
    full_name_comments = forms.CharField(label='Enter your reasoning here',
                                         widget=custom_field_widgets.Textarea(attrs={'cols': '40', 'rows': '3'}),
                                         required=False)

    date_of_birth_declare = forms.BooleanField(label='This information is correct',
                                               widget=custom_field_widgets.CustomCheckboxInput, required=False)
    date_of_birth_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                             required=False)

    relationship_declare = forms.BooleanField(label='This information is correct',
                                              widget=custom_field_widgets.CustomCheckboxInput, required=False)
    relationship_comments = forms.CharField(label='Enter your reasoning here', widget=custom_field_widgets.Textarea,
                                            required=False)

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


class SearchForm(GOVUKForm):
    """
    GOV.UK form for the Your login and contact details: email page
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    query = forms.CharField(label='Search all fields', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your login and contact details: email form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        super(SearchForm, self).__init__(*args, **kwargs)

    def clean_query(self):
        query = self.cleaned_data['query']
        if len(query) < 3:
            raise forms.ValidationError('Please enter a keyword that is greater than 2 characters')
        if len(query) == 0:
            raise forms.ValidationError('This field is required')
        return query
