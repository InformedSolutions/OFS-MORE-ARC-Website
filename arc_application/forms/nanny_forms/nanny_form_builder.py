from django import forms

from arc_application import custom_field_widgets


class NannyARCForm(forms.Form):
    auto_replace_widgets = True

    def __init__(self, *args, **kwargs):
        fields_to_add = kwargs.pop('form_fields')
        super(NannyARCForm, self).__init__(*args, **kwargs)

        for field_name, field_value in fields_to_add.items():
            self.fields[field_name] = field_value


class NannyFormBuilder:
    """
    Builder class for generating Nanny ARC forms dynamically, given a list of fields required for that form.
    :return form with a _declare and _comments field for each field in the list passed. These are the fields for
            flagging and commenting upon a field of submitted data.
    """
    def __init__(self, field_names):
        self.field_names = field_names
        self.form_fields = dict()
        self.checkboxes = None
        self.form = None

    def create_form(self):
        self.get_form_fields()
        self.update_checkbox_widgets()
        self.form = NannyARCForm(form_fields=self.form_fields)
        return self.form

    def get_form_fields(self):

        bool_field = forms.BooleanField(
            label='This information is correct',
            widget=custom_field_widgets.CustomCheckboxInput,
            required=False
        )
        char_field = forms.CharField(
            label='Enter your reasoning',
            help_text='(Tip: be clear and concise)',
            widget=custom_field_widgets.Textarea,
            required=False
        )

        for field in self.field_names:
            self.form_fields[field + '_declare'] = bool_field
            self.form_fields[field + '_comments'] = char_field

    def update_checkbox_widgets(self):
        checkboxes = [(field, name[:-8]) for name, field in self.form_fields.items() if name[-8:] == '_declare']

        for box in checkboxes:
            box[0].widget.attrs.update(
                {
                    'data_target': box[1],
                    'aria-controls': box[1],
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


dbs_form = NannyFormBuilder(dbs_check_fields).create_form()
