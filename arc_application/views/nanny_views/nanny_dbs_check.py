from .nanny_form_view import NannyARCFormView
from ...forms.nanny_forms.nanny_form_builder import DBSForm
from ...services.db_gateways import NannyGatewayActions


class NannyDbsCheckSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_insurance_cover_summary'
    task_for_review = 'dbs_review'
    verbose_task_name = 'Criminal record checks'
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
        dbs_record = nanny_actions.read('dbs-check', params={'application_id': application_id}).record


        dbs_page_link = 'dbs:Capita-DBS-Details-View'


        lived_abroad = dbs_record['lived_abroad']
        is_ofsted_dbs = dbs_record['is_ofsted_dbs']
        on_dbs_update_service = dbs_record['on_dbs_update_service']
        dbs_number = dbs_record['dbs_number']
        enhanced_check = dbs_record['enhanced_check']
        within_three_months = dbs_record['within_three_months']


        form = self.get_form()

        context = {
            'application_id': application_id,
            'title': 'Review: ' + self.verbose_task_name,
            'form': form,
            'change_link': 'nanny_dbs_summary',
            'rows': [
                {
                    'id': 'lived_abroad',
                    'name': 'Have you lived outside of the UK in the last 5 years?',
                    'info': lived_abroad,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'declare': form['lived_abroad_declare'] if hasattr(self, 'request') else '',
                    'comments': form['lived_abroad_comments'],
                },
                {
                    'id': 'is_ofsted_dbs',
                    'name': 'Did they get their DBS check from the Ofsted DBS application website?',
                    'info': is_ofsted_dbs
                },
                {
                    'id': 'within_three_months',
                    'name': 'Is it dated within the last 3 months?',
                    'info': within_three_months,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'hidden': not bool(is_ofsted_dbs)
                },
                {
                    'id': 'dbs_number',
                    'name': 'DBS certificate number',
                    'info': dbs_number,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'declare': form['dbs_number_declare'] if hasattr(self, 'request') else '',
                    'comments': form['dbs_number_comments']
                },
                {
                    'id': 'enhanced_check',
                    'name': 'Is it an enhanced DBS check for home-based childcare?',
                    'info': enhanced_check,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'declare': form['enhanced_check_declare'] if hasattr(self, 'request') else '',
                    'comments': form['enhanced_check_comments'],
                    'hidden': bool(is_ofsted_dbs)
                },
                {
                    'id': 'on_dbs_update_service',
                    'name': 'Are you on the DBS update service?',
                    'info': on_dbs_update_service,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'declare': form['on_dbs_update_service_declare'] if hasattr(self, 'request') else '',
                    'comments': form['on_dbs_update_service_comments'],
                    'hidden': bool(is_ofsted_dbs) and bool(within_three_months)
                }
            ]
        }

        return context
