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

        lived_abroad = dbs_record['lived_abroad']
        is_ofsted_dbs = dbs_record['is_ofsted_dbs']
        enhanced_check = dbs_record['enhanced_check']
        on_dbs_update_service = dbs_record['on_dbs_update_service']
        within_three_months = dbs_record['within_three_months']
        dbs_number = dbs_record['dbs_number']

        if is_ofsted_dbs is True:
            dbs_page_link = 'dbs:Capita-DBS-Details-View'
        elif is_ofsted_dbs is False:
            dbs_page_link = 'dbs:Non-Capita-DBS-Details-View'
        else:
            raise ValueError('The "is_ofsted_dbs" value does not equal either True or False.')

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
                    'id': 'enhanced_check',
                    'name': 'Do you have an enhanced DBS check for home-based childcare?',
                    'info': enhanced_check,
                    'declare': form['enhanced_check_declare'] if hasattr(self, 'request') else '',
                    'comments': form['enhanced_check_comments'],
                    'hidden': is_ofsted_dbs,
                },
                {
                    'id': 'on_dbs_update_service',
                    'name': 'Are you on the DBS update service?',
                    'info': on_dbs_update_service,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'declare': form['on_dbs_update_service_declare'] if hasattr(self, 'request') else '',
                    'comments': form['on_dbs_update_service_comments'],
                    'hidden': (is_ofsted_dbs and within_three_months) or (not is_ofsted_dbs and not enhanced_check),
                },
                {
                    'id': 'dbs_number',
                    'name': 'DBS certificate number',
                    'info': dbs_number,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'declare': form['dbs_number_declare'] if hasattr(self, 'request') else '',
                    'comments': form['dbs_number_comments'],
                }
            ]
        }

        return context
