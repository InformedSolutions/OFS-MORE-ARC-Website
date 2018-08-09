from django import forms

from arc_application import custom_field_widgets


class NannyFormBuilder:
    """
    Builder class for generating Nanny ARC forms dynamically, given a list of fields required for that form.
    :return form with a _declare and _comments field for each field in the list passed. These are the fields for
            flagging and commenting upon a field of submitted data.
    """
    def __init__(self, fields):
        self.fields = fields
        self.form = None

    def create_form(self):
        self.form = forms.Form()
        self.form.auto_replace_widgets = True
        self.set_form_fields()
        self.update_widgets()
        return self.form

    def set_form_fields(self):

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

        for field in self.fields:
            setattr(self.form, field + '_declare', bool_field)
            setattr(self.form, field + '_comments', char_field)

    def update_widgets(self):
        checkboxes = [(getattr(self.form, field + '_declare'), field) for field in self.fields]

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

# 'Do you know where you will be working?'
# 'Do you live and work at the same address?'

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
