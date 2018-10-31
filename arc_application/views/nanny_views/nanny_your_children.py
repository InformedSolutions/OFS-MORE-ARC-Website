from .nanny_form_view import NannyARCFormView
from ...forms.nanny_forms.nanny_form_builder import ChildrenLivingWithYouForm, YourChildrenFormset
from ...services.db_gateways import NannyGatewayActions


class NannyYourChildrenSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_childcare_address_summary'
    task_for_review = 'your_children_review'
    verbose_task_name = 'Your children'
    form_class = [ChildrenLivingWithYouForm, YourChildrenFormset]

    def get_context_data(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        self.application_id = application_id
        nanny_actions = NannyGatewayActions()

        children_records = nanny_actions.list('your-children', params={'application_id': application_id}).record

        children_living_wth_applicant = 'TEMPORARY CHILD NAME'  # TODO: Add logic for setting row value.

        children_living_with_you_form, children_formset = self.get_forms()

        context = {
            'application_id': application_id,
            'title': 'Review: ' + self.verbose_task_name,
            'rows': [
                {
                    'id': 'children_living_with_applicant_selection',
                    'name': 'Your children\'s addresses',
                    'info': children_living_wth_applicant,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'declare': children_living_with_you_form['children_living_with_applicant_selection_declare'] if hasattr(self, 'request') else '',
                    'comments': children_living_with_you_form['children_living_with_applicant_selection_comments']
                },
                {
                    'id': 'your_children_details',
                    'info': children_records,
                    'formset': children_formset
                }
            ]
        }

        return context
