from django import forms
from django.forms import formset_factory
from django.utils.functional import cached_property
from govuk_forms.forms import GOVUKForm

from arc_application.widgets import CustomCheckboxInput, Textarea


def get_declare_comments_tuples_list(cleaned_data):
    return [(key, f'{key[:-8]}_comments') for key, val in cleaned_data.items() if
            key.endswith('_declare')]


class NannyFormBuilder:
    """
    Builder class for generating Nanny ARC forms dynamically, given a list of fields required for that form.
    :return: form with a {{field_name}}_declare and {{field_name}}_comments field for each field in the list passed.
             These are the fields for flagging and commenting upon a field of submitted data.
    """

    def __init__(self, field_data, api_endpoint_name=None):
        self.field_data = field_data
        self.field_names, self.label_names = zip(*field_data.items())
        self.form_fields = dict()
        self._api_endpoint_name = api_endpoint_name

    def get_api_endpoint_name(self):
        if self._api_endpoint_name is not None:
            return self._api_endpoint_name
        else:
            raise AttributeError(
                'You must supply the api endpoint of the table for which the ArcComment will be saved.')

    def create_form(self):
        self.get_form_fields()
        self.update_checkbox_field_widgets()

        class NannyARCForm(GOVUKForm):
            # __name__ = 'NannyARCForm'
            auto_replace_widgets = True
            field_names = self.field_names
            api_endpoint_name = self.get_api_endpoint_name()
            field_label_classes = 'form-label-bold'

            ERROR_MESSAGE_BLANK_COMMENT = 'You must give reasons'

            def clean(self):
                """
                Cleans _comment fields to raise validation message if their corresponding _declare
                field is set to True and the comment is blank.
                :return: cleaned_data
                """
                cleaned_data = self.cleaned_data

                declare_comments_fields = get_declare_comments_tuples_list(cleaned_data)
                for declare_field_name, comment_field_name in declare_comments_fields:
                    declare_value = cleaned_data.get(declare_field_name, None)
                    comment_value = cleaned_data.get(comment_field_name, None)

                    if declare_value is True and comment_value is not None and comment_value == '':
                        self.add_error(declare_field_name, self.ERROR_MESSAGE_BLANK_COMMENT)

                return super().clean()

        for field_name, field in self.form_fields.items():
            NannyARCForm.base_fields[field_name] = field

        return NannyARCForm

    def create_formset(self):
        Formset = formset_factory(self.create_form(), extra=0)

        @cached_property
        def _overrriden_forms(self):
            forms = [self._construct_form(i, **self.get_form_kwargs(i)) for i in range(self.total_form_count())]

            for index, form in enumerate(forms):
                for field_name in self.form.field_names:
                    form.fields[field_name + '_declare'].widget.attrs.update(
                        {
                            'data_target': field_name + '_' + str(index + 1),
                            'aria-controls': field_name + '_' + str(index + 1),
                            'aria-expanded': 'false'
                        }
                    )

            return forms

        Formset.forms = _overrriden_forms

        return Formset

    def get_form_fields(self):
        for field_name, field_label in self.field_data.items():
            self.form_fields[field_name + '_declare'] = forms.BooleanField(
                label=field_label,
                widget=CustomCheckboxInput,
                required=False
            )
            self.form_fields[field_name + '_comments'] = forms.CharField(
                label='Enter your reasoning',
                help_text='(Tip: be clear and concise)',
                widget=Textarea,
                required=False,
                max_length=500
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

# children_living_with_you_fields = [
# 'children_living_with_applicant_selection',
# ]

# ChildrenLivingWithYouForm = NannyFormBuilder(children_living_with_you_fields,
# api_endpoint_name = 'application').create_form()
