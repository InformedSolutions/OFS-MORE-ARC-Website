from arc_application.forms.nanny_forms.nanny_form_builder import FirstAidForm
from arc_application.services.db_gateways import NannyGatewayActions
from arc_application.views.nanny_views.nanny_form_view import NannyARCFormView


class NannyFirstAidTrainingSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_childcare_training_summary'
    task_for_review = 'first_aid_review'
    form_class = FirstAidForm

    def get_context_data(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        nanny_actions = NannyGatewayActions()
        first_aid_dict = nanny_actions.read('first-aid',
                                            params={'application_id': application_id}).record

        training_organisation = first_aid_dict['training_organisation']
        training_course_title = first_aid_dict['course_title']
        date_course_completed = first_aid_dict['course_date']

        form = self.get_form()

        context = {
            'application_id': application_id,
            'title': 'Review: First aid training',
            'form': form,
            'rows': [
                {
                    'id': 'training_organisation',
                    'name': 'Training organisation',
                    'info': training_organisation,
                    'declare': form['training_organisation_declare'],
                    'comments': form['training_organisation_comments']
                },
                {
                    'id': 'course_title',
                    'name': 'Title of training course',
                    'info': training_course_title,
                    'declare': form['course_title_declare'],
                    'comments': form['course_title_comments']
                },
                {
                    'id': 'course_date',
                    'name': 'Date you completed the course',
                    'info': date_course_completed,
                    'declare': form['course_date_declare'],
                    'comments': form['course_date_comments']
                }
            ]
        }

        return context
