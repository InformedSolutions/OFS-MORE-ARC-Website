from ...services.db_gateways import NannyGatewayActions
from ...forms.nanny_forms.nanny_form_builder import DBSForm
from .nanny_form_view import NannyARCFormView


class NannyDbsCheckSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_insurance_cover_summary'
    task_for_review = 'dbs_review'
    form_class = DBSForm

    def get_context_data(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        self.application_id = application_id
        # Get nanny information
        nanny_actions = NannyGatewayActions()
        dbs_check_dict = nanny_actions.read('dbs-check', params={'application_id': application_id}).record

        dbs_certificate_number = dbs_check_dict['dbs_number']
        criminal_bool = dbs_check_dict['convictions']

        form = self.get_form()

        context = {
            'application_id': application_id,
            'title': 'Review: Criminal record (DBS) check',
            'form': form,
            'rows': [
                {
                    'id': 'dbs_number',
                    'name': 'DBS certificate number',
                    'info': dbs_certificate_number,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'declare': form['dbs_number_declare'] if hasattr(self, 'request') else '',
                    'comments': form['dbs_number_comments'],
                },
                {
                    'id': 'convictions',
                    'name': 'Do you have any criminal cautions or convictions?',
                    'info': criminal_bool,
                    'declare': form['convictions_declare'] if hasattr(self, 'request') else '',
                    'comments': form['convictions_comments'],
                }
            ]
        }

        return context
