from .nanny_form_view import NannyARCFormView
from ...forms.nanny_forms.nanny_form_builder import YourChildrenFormset
from ...services.db_gateways import NannyGatewayActions


class NannyYourChildrenSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_childcare_address_summary'
    task_for_review = 'your_children_review'
    verbose_task_name = 'Your children'
    form_class = YourChildrenFormset

    def get_context_data(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        self.application_id = application_id
        nanny_actions = NannyGatewayActions()

        children_records = nanny_actions.list('your-children', params={'application_id': application_id}).record

        children_formset = self.get_form()

        context = {
            'application_id': application_id,
            'title': 'Review: ' + self.verbose_task_name,
            'rows': [
                {
                    'id': 'your_children_details',
                    'name': 'Your children',
                    'info': children_records,
                    'formset': children_formset
                }
            ]
        }

        return context
