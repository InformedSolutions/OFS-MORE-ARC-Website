from arc_application.forms.nanny_forms.nanny_form_builder import ChildcareTrainingForm
from arc_application.services.db_gateways import NannyGatewayActions
from arc_application.views.nanny_views.nanny_form_view import NannyARCFormView


class NannyChildcareTrainingSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_dbs_summary'
    task_for_review = 'childcare_training_review'
    form_class = ChildcareTrainingForm

    def get_context_data(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        nanny_actions = NannyGatewayActions()
        childcare_training_dict = nanny_actions.read('childcare-training',
                                                     params={'application_id': application_id}).record

        level_2_training = childcare_training_dict['level_2_training']
        common_core_training = childcare_training_dict['common_core_training']

        form = self.get_form()

        context = {
            'application_id': application_id,
            'title': 'Review: Childcare training',
            'form': form,
            'rows': [
                {
                    'id': 'level_2_training',
                    'name': 'Do you have a childcare qualification?',
                    'info': level_2_training,
                    'declare': form['level_2_training_declare'],
                    'comments': form['level_2_training_comments'],
                },
                {
                    'id': 'common_core_training',
                    'name': 'Have you had common core training?',
                    'info': common_core_training,
                    'declare': form['common_core_training_declare'],
                    'comments': form['common_core_training_comments'],
                }
            ]
        }

        return context