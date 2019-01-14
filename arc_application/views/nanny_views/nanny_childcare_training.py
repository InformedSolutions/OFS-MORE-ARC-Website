from ...forms.nanny_forms.nanny_form_builder import ChildcareTrainingForm
from ...services.db_gateways import NannyGatewayActions
from .nanny_form_view import NannyARCFormView


class NannyChildcareTrainingSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_dbs_summary'
    task_for_review = 'childcare_training_review'
    verbose_task_name = 'Childcare training'
    form_class = ChildcareTrainingForm

    def get_context_data(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        self.application_id = application_id
        nanny_actions = NannyGatewayActions()
        childcare_training_dict = nanny_actions.read('childcare-training',
                                                     params={'application_id': application_id}).record

        level_2_training = childcare_training_dict['level_2_training']
        common_core_training = childcare_training_dict['common_core_training']

        if level_2_training and common_core_training:
            childcare_training = 'Childcare qualification (level 2 or higher) and training in common core skills'
        elif level_2_training:
            childcare_training = 'Childcare qualification (level 2 or higher)'
        else:
            childcare_training = 'Training in common core skills'

        form = self.get_form()

        context = {
            'application_id': application_id,
            'title': 'Review: ' + self.verbose_task_name,
            'form': form,
            'change_link': 'nanny_childcare_training_summary',
            'rows': [
                {
                    'id': 'childcare_training',
                    'name': 'What type of childcare course have you completed?',
                    'info': childcare_training,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'declare': form['childcare_training_declare'] if hasattr(self, 'request') else '',
                    'comments': form['childcare_training_comments']
                },
            ]
        }

        return context