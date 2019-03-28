from ...forms.nanny_forms.nanny_forms import FirstAidForm
from ...forms.nanny_forms.form_data import FIRST_AID_TRAINING_DATA
from ...services.db_gateways import NannyGatewayActions
from .nanny_form_view import NannyARCFormView


class NannyFirstAidTrainingSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_childcare_training_summary'
    task_for_review = 'first_aid_review'
    verbose_task_name = 'First aid training'
    form_class = FirstAidForm

    def get_context_data(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        self.application_id = application_id
        nanny_actions = NannyGatewayActions()
        first_aid_dict = nanny_actions.read('first-aid',
                                            params={'application_id': application_id}).record

        training_organisation = first_aid_dict['training_organisation']
        training_course_title = first_aid_dict['course_title']
        date_course_completed = first_aid_dict['course_date']
        date_course_completed_list = date_course_completed.split('-')
        date_course_completed_formatted = date_course_completed_list[2] + '/' + date_course_completed_list[1] + '/' + date_course_completed_list[0]

        form = self.get_form()

        context = {
            'application_id': application_id,
            'title': 'Review: ' + self.verbose_task_name,
            'change_link': 'nanny_first_aid_training_summary',
            'form': form,
            'rows': [
                {
                    'id': 'training_organisation',
                    'name': FIRST_AID_TRAINING_DATA['training_organisation'],
                    'info': training_organisation,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'declare': form['training_organisation_declare'] if hasattr(self, 'request') else '',
                    'comments': form['training_organisation_comments']
                },
                {
                    'id': 'course_title',
                    'name': FIRST_AID_TRAINING_DATA['course_title'],
                    'info': training_course_title,
                    'declare': form['course_title_declare'] if hasattr(self, 'request') else '',
                    'comments': form['course_title_comments']
                },
                {
                    'id': 'course_date',
                    'name': FIRST_AID_TRAINING_DATA['course_date'],
                    'info': date_course_completed_formatted,
                    'declare': form['course_date_declare'] if hasattr(self, 'request') else '',
                    'comments': form['course_date_comments']
                }
            ]
        }

        return context
