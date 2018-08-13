from django import forms

from arc_application import custom_field_widgets


class NannyFormBuilder:
    """
    Builder class for generating Nanny ARC forms dynamically, given a list of fields required for that form.
    :return: form with a {{field_name}}_declare and {{field_name}}_comments field for each field in the list passed.
             These are the fields for flagging and commenting upon a field of submitted data.
    """
    def __init__(self, field_names, pk_field_name=None, api_endpoint_name=None):
        self.field_names = field_names
        self.form_fields = dict()
        self._pk_field_name = pk_field_name
        self._api_endpoint_name = api_endpoint_name

    def get_pk_field_name(self):
        if self._pk_field_name is not None:
            return self._pk_field_name
        else:
            raise NotImplementedError('You must supply the pk_name of the table for which the ArcComment will be saved.')

    def get_api_endpoint_name(self):
        if self._api_endpoint_name is not None:
            return self._api_endpoint_name
        else:
            raise NotImplementedError('You must supply the pk_name of the table for which the ArcComment will be saved.')

    def create_form(self):
        self.get_form_fields()
        self.update_checkbox_field_widgets()

        class NannyARCForm(forms.Form):
            auto_replace_widgets = True
            field_names = self.field_names
            pk_field_name = self.get_pk_field_name()
            api_endpoint_name = self.get_api_endpoint_name()

        for field_name, field in self.form_fields.items():
            NannyARCForm.base_fields[field_name] = field

        return NannyARCForm

    def get_form_fields(self):
        for field in self.field_names:
            self.form_fields[field + '_declare'] = forms.BooleanField(
                                                        label='This information is correct',
                                                        widget=custom_field_widgets.CustomCheckboxInput,
                                                        required=False
                                                    )
            self.form_fields[field + '_comments'] = forms.CharField(
                                                        label='Enter your reasoning',
                                                        help_text='(Tip: be clear and concise)',
                                                        widget=custom_field_widgets.Textarea,
                                                        required=False
                                                    )

    def update_checkbox_field_widgets(self):
        checkboxes = [(field, name[:-8]) for name, field in self.form_fields.items() if name[-8:] == '_declare']

        for box in checkboxes:
            declare_field, target_html_id_tag = box
            declare_field.widget.attrs.update(
                {
                    'data_target': target_html_id_tag,
                    'aria-controls': target_html_id_tag,
                    'aria-expanded': 'false'
                }
            )


sign_in_form_fields = [
    'email',
    'mobile_phone',
    'other_phone',
]

personal_details_fields = [
    'name',
    'date_of_birth',
    'lived_abroad',
]

home_address_fields = [
    'home_address',
]

childcare_address_fields = [
    'address_1',
    'address_2',
    'address_3',
    'address_4',
]

first_aid_training_fields = [
    'training_organisation',
    'course_title',
    'course_date',
]

childcare_training_fields = [
    'level_2_training',
    'common_core_training',
]

dbs_check_fields = [
    'dbs_number',
    'convictions',
]

insurance_cover_fields = [
    'public_liability_insurance',
]


PersonalDetailsForm     = NannyFormBuilder(personal_details_fields, pk_field_name='personal_detail_id', api_endpoint_name='applicant-personal-details').create_form()
HomeAddressForm         = NannyFormBuilder(home_address_fields, pk_field_name='home_address_id', api_endpoint_name='applicant-home-address').create_form()
childcare_address_form  = None
FirstAidForm            = NannyFormBuilder(first_aid_training_fields, pk_field_name='first_aid_id', api_endpoint_name='first-aid').create_form()
ChildcareTrainingForm   = NannyFormBuilder(childcare_training_fields, pk_field_name='childcare_training_id', api_endpoint_name='childcare-training').create_form()
DBSForm                 = NannyFormBuilder(dbs_check_fields, pk_field_name='dbs_id', api_endpoint_name='dbs-check').create_form()
InsuranceCoverForm      = NannyFormBuilder(insurance_cover_fields, pk_field_name='insurance_cover_id', api_endpoint_name='insurance-cover').create_form()
