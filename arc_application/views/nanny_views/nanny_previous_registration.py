from ...forms.nanny_forms.nanny_form_builder import PreviousRegistrationForm
from arc_application.services.db_gateways import NannyGatewayActions

from .nanny_form_view import NannyARCFormView


class NannyPreviousRegistrationView(NannyARCFormView):
    template_name = 'nanny_add_previous_registration_template.html'
    success_url = 'nanny_personal_details_summary'
    #task_for_review = 'personal_details_review'
    verbose_task_name = 'Previous Registration'
    form_class = PreviousRegistrationForm

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
        within_three_months = dbs_record['within_three_months']


        lived_abroad = dbs_record['lived_abroad']
        is_ofsted_dbs = dbs_record['is_ofsted_dbs']
        on_dbs_update_service = dbs_record['on_dbs_update_service']
        dbs_number = dbs_record['dbs_number']
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
                    'hidden': not is_ofsted_dbs
                },
            ]
        }

        return context