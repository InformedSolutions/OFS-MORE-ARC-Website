from django import forms

from arc_application import custom_field_widgets


class NannyARCForm(forms.Form):
    auto_replace_widgets = True

    def __init__(self, *args, **kwargs):
        fields_to_add          = kwargs.pop('form_fields')
        self.pk_field_name     = kwargs.pop('pk_field_name')
        self.api_endpoint_name = kwargs.pop('api_endpoint_name')

        super(NannyARCForm, self).__init__(*args, **kwargs)

        for field_name, field_value in fields_to_add.items():
            self.fields[field_name] = field_value


class NannyFormBuilder:
    """
    Builder class for generating Nanny ARC forms dynamically, given a list of fields required for that form.
    :return form with a _declare and _comments field for each field in the list passed. These are the fields for
            flagging and commenting upon a field of submitted data.
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
        return NannyARCForm(form_fields=self.form_fields,
                            pk_field_name=self.get_pk_field_name(),
                            api_endpoint_name=self.get_api_endpoint_name())

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
    'home_address',
    'lived_abroad',
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


personal_details_form   = None  # NannyFormBuilder(personal_details_fields, 'personal_detail_id').create_form()
childcare_address_form  = None
first_aid_form          = None  # NannyFormBuilder(first_aid_training_fields, 'first_aid_id').create_form()
childcare_training_form = None  # NannyFormBuilder(childcare_training_fields, 'childcare_training_id').create_form()
dbs_form                = NannyFormBuilder(dbs_check_fields, pk_field_name='dbs_id', api_endpoint_name='dbs-check').create_form()
insurance_cover_form    = None  # NannyFormBuilder(insurance_cover_fields, 'insurance_cover_id').create_form()
