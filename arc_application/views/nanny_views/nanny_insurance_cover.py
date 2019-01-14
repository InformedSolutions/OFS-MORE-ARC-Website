from ...forms.nanny_forms.nanny_form_builder import InsuranceCoverForm
from ...services.db_gateways import NannyGatewayActions
from .nanny_form_view import NannyARCFormView


class NannyInsuranceCoverSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_task_list'
    task_for_review = 'insurance_cover_review'
    verbose_task_name = 'Insurance cover'
    form_class = InsuranceCoverForm

    def get_context_data(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        self.application_id = application_id
        nanny_actions = NannyGatewayActions()
        insurance_cover_dict = nanny_actions.read('insurance-cover',
                                                  params={'application_id': application_id}).record

        insurance_bool = insurance_cover_dict['public_liability']

        form = self.get_form()

        context = {
            'application_id': application_id,
            'title': 'Review: ' + self.verbose_task_name,
            'form': form,
            'change_link': 'nanny_insurance_cover_summary',
            'rows': [
                {
                    'id': 'public_liability',
                    'name': 'Do you have public liability insurance?',
                    'info': insurance_bool,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'declare': form['public_liability_declare'] if hasattr(self, 'request') else '',
                    'comments': form['public_liability_comments']
                }
            ]
        }

        return context