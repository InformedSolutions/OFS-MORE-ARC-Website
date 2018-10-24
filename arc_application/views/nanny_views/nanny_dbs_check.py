from .nanny_form_view import NannyARCFormView
from ...forms.nanny_forms.nanny_form_builder import DBSForm
from ...services.db_gateways import NannyGatewayActions


class NannyDbsCheckSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_insurance_cover_summary'
    task_for_review = 'dbs_review'
    verbose_task_name = 'Criminal record (DBS) check'
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

        if dbs_record['is_ofsted_dbs']:
            dbs_page_link = 'dbs:Capita-DBS-Details-View'
        elif not dbs_record['is_ofsted_dbs']:
            dbs_page_link = 'dbs:Non-Capita-DBS-Details-View'
        else:
            raise ValueError('The "is_ofsted_dbs" value does not equal either True or False.')

        lived_abroad = dbs_record['lived_abroad']
        is_ofsted_dbs = dbs_record['is_ofsted_dbs']
        on_dbs_update_service = dbs_record['on_dbs_update_service']
        dbs_number = dbs_record['dbs_number']
        has_convictions = dbs_record['has_convictions']

        form = self.get_form()

        context = {
            'application_id': application_id,
            'title': 'Review: ' + self.verbose_task_name,
            'form': form,
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
                    'name': 'Do you have an Ofsted DBS Check?',
                    'info': is_ofsted_dbs,
                    'declare': form['is_ofsted_dbs_declare'] if hasattr(self, 'request') else '',
                    'comments': form['is_ofsted_dbs_comments'],
                },
                {
                    'id': 'on_dbs_update_service',
                    'name': 'Are you on the DBS update service?',
                    'info': on_dbs_update_service,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'declare': form['on_dbs_update_service_declare'] if hasattr(self, 'request') else '',
                    'comments': form['on_dbs_update_service_comments'],
                    'hidden': bool(is_ofsted_dbs)
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
                    'id': 'has_convictions',
                    'name': 'Do you have any criminal cautions or convictions?',
                    'info': has_convictions,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'declare': form['has_convictions_declare'] if hasattr(self, 'request') else '',
                    'comments': form['has_convictions_comments'],
                    'hidden': not bool(is_ofsted_dbs)
                }
            ]
        }

        return context
