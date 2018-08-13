from arc_application.services.db_gateways import NannyGatewayActions

from arc_application.forms.nanny_forms.nanny_form_builder import dbs_form

from arc_application.views.nanny_views.nanny_form_view import NannyARCFormView


class NannyDbsCheckSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_task_list'  # TODO - Update to 'nanny_insurance_cover_summary' once functional.
    task_for_review = 'dbs_review'
    form = dbs_form

    def get_context_data(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        # Get nanny information
        nanny_actions = NannyGatewayActions()
        dbs_check_dict = nanny_actions.read('dbs-check', params={'application_id': application_id}).record

        dbs_certificate_number = dbs_check_dict['dbs_number']
        criminal_bool = dbs_check_dict['convictions']

        # Set up context
        context = {
            'application_id': application_id,
            'title': 'Review: Criminal record (DBS) check',
            'form': dbs_form,
            'rows': [
                {
                    'id': 'dbs_number',
                    'name': 'DBS certificate number',
                    'info': dbs_certificate_number,
                    'declare': dbs_form['dbs_number_declare'],
                    'comments': dbs_form['dbs_number_comments'],
                },
                {
                    'id': 'convictions',
                    'name': 'Do you have any criminal cautions or convictions?',
                    'info': criminal_bool,
                    'declare': dbs_form['convictions_declare'],
                    'comments': dbs_form['convictions_comments'],
                }
            ]
        }

        return context
