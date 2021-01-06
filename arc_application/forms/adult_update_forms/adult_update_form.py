import re
import uuid

from django import forms
from django.conf import settings
from django.forms import ModelForm
from ... import widgets
from govuk_forms.forms import GOVUKForm
from govuk_forms.widgets import InlineRadioSelect, NumberInput, Select

class NewAdultForm(GOVUKForm):
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
                                     required=False, max_length=250)

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
        help_text='Known to council (Tip: be clear and concise)',
        widget=widgets.Textarea, required=False,
        max_length=500)

    reasons_known_to_social_services_pith_comments = forms.CharField(label='Tell us why',
                                                                     help_text='(Tip: be clear and concise)',
                                                                     widget=widgets.Textarea,
                                                                     required=False, max_length=500)
    # SoW8 Additional Fields
    current_name_declare = forms.BooleanField(label='Current name',
                                           widget=widgets.CustomCheckboxInput, required=False)
    current_name_comments = forms.CharField(label='Current name comments',
                                         help_text='(Tip: be clear and concise)',
                                         widget=widgets.Textarea,
                                         required=False, max_length=500)
    known_by_other_names_declare = forms.BooleanField(label='Known by other names',
                                              widget=widgets.CustomCheckboxInput, required=False)
    known_by_other_names_comments = forms.CharField(label='Known by other names comments',
                                            help_text='(Tip: be clear and concise)',
                                            widget=widgets.Textarea,
                                            required=False, max_length=500)
    name_history_declare = forms.BooleanField(label='Name history',
                                                      widget=widgets.CustomCheckboxInput, required=False)
    name_history_comments = forms.CharField(label='Name history comments',
                                                    help_text='(Tip: be clear and concise)',
                                                    widget=widgets.Textarea,
                                                    required=False, max_length=500)
    PITH_address_moved_in_declare = forms.BooleanField(label='Current address moved in',
                                              widget=widgets.CustomCheckboxInput, required=False)
    PITH_address_moved_in_comments = forms.CharField(label='Current address moved in comments',
                                            help_text='(Tip: be clear and concise)',
                                            widget=widgets.Textarea,
                                            required=False, max_length=500)
    address_history_declare = forms.BooleanField(label='Address history',
                                                      widget=widgets.CustomCheckboxInput, required=False)
    address_history_comments = forms.CharField(label='Address history comments',
                                                    help_text='(Tip: be clear and concise)',
                                                    widget=widgets.Textarea,
                                                    required=False, max_length=500)


    # This is the id appended to all htmls names ot make the individual form instance unique, this is given a value in
    # the init
    instance_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super(NewAdultForm, self).__init__(*args, **kwargs)
        # Create unique id value and populate the instance_id field with it
        id_value = str(uuid.uuid4())
        self.fields['instance_id'].initial = id_value
        # Make all checkbox names refer the the name with the correct instance id, making each conditional reveal unique
        checkboxes = [
            ((self.fields['health_check_status_declare']), 'health_check_status' + id_value),
            #((self.fields['full_name_declare']), 'full_name' + id_value),
            ((self.fields['date_of_birth_declare']), 'date_of_birth' + id_value),
            ((self.fields['relationship_declare']), 'relationship' + id_value),
            ((self.fields['email_declare']), 'email' + id_value),
            ((self.fields['PITH_same_address_declare']), 'PITH_same_address' + id_value),
            ((self.fields['dbs_certificate_number_declare']), 'dbs_certificate_number' + id_value),
            ((self.fields['enhanced_check_declare']), 'enhanced_check' + id_value),
            ((self.fields['on_update_declare']), 'on_update' + id_value),
            ((self.fields['lived_abroad_declare']), 'lived_abroad' + id_value),
            ((self.fields['military_base_declare']), 'military_base' + id_value),
            # SoW8 Additional
            ((self.fields['current_name_declare']), 'current_name' + id_value),
            ((self.fields['known_by_other_names_declare']), 'known_by_other_names' + id_value),
            ((self.fields['name_history_declare']), 'name_history' + id_value),
            ((self.fields['PITH_address_moved_in_declare']), 'PITH_address_moved_in' + id_value),
            ((self.fields['address_history_declare']), 'address_history' + id_value),
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

    def clean_PITH_same_address_comments(self):
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

    # SoW8 Additional Fields

    def clean_current_name_comments(self):
        """
        PITH current_name comments validation
        :return: string
        """
        return self.helper_clean('current_name')

    def clean_known_by_other_names_comments(self):
        """
        PITH known_by_other_names comments validation
        :return: string
        """
        return self.helper_clean('known_by_other_names')

    def clean_name_history_comments(self):
        """
        PITH name_history comments validation
        :return: string
        """
        return self.helper_clean('name_history')

    def clean_address_history_comments(self):
        """
        PITH address_history comments validation
        :return: string
        """
        return self.helper_clean('address_history')

    def clean_PITH_address_moved_in_comments(self):
        """
        PITH PITH_address_moved_in comments validation
        :return: string
        """
        return self.helper_clean('PITH_address_moved_in')

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