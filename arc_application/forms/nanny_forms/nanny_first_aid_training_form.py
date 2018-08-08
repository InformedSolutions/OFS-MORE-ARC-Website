from django import forms
from govuk_forms.forms import GOVUKForm

from arc_application import custom_field_widgets
from arc_application.review_util import populate_initial_values

class FirstAidTrainingForm(GOVUKForm):
    """
    GOV.UK form for the First Aid Training Form
    """
    # Customisations:
    auto_replace_widgets = True

    # General Params
    declare_params = {'label': 'This information is correct',
                      'widget': custom_field_widgets.CustomCheckboxInput,
                      'required': False}

    comments_params = {'label': 'Enter your reasoning',
                       'help_text': '(Tip: be clear and concise)',
                       'widget': custom_field_widgets.Textarea,
                       'required': False}

    first_aid_training_organisation_declare = forms.BooleanField(**declare_params)
    first_aid_training_organisation_comments = forms.CharField(**comments_params)

    title_of_training_course_declare = forms.BooleanField(**declare_params)
    title_of_training_course_comments = forms.CharField(**comments_params)

    course_date_declare = forms.BooleanField(**declare_params)
    course_date_comments = forms.CharField(**comments_params)

    checkboxes = [(first_aid_training_organisation_declare, 'first_aid_training_organisation'),
                  (title_of_training_course_declare, 'title_of_training_course'),
                  (course_date_declare, 'course_date')]

    for box in checkboxes:
        declare, target_field = box
        declare.widget.attrs.update({'data_target': target_field,
                                    'aria-controls': target_field,
                                    'aria-expanded': 'false'}, )

    def __init__(self, *args, **kwargs):
        self.table_keys = kwargs.pop('table_keys')
        super(FirstAidTrainingForm, self).__init__(*args, **kwargs)
        populate_initial_values(self)

