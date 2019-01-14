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

        children_living_with_applicant = [child for child in children_records if child['lives_with_applicant']]
        children_living_with_applicant_temp_store = []

        # Create a list of names of children that live with the applicant
        for child in children_living_with_applicant:
            child_name = str(child['first_name']) + " " + str(child['last_name'])
            children_living_with_applicant_temp_store.append(child_name)

        # Create list of names for the table row
        if len(children_living_with_applicant_temp_store) == 0:
            children_living_with_you_response_string = 'None'
        else:
            children_living_with_you_response_string = ", ".join(children_living_with_applicant_temp_store)

        children_living_with_you_form, children_formset = self.get_forms()

        context = {
            'application_id': application_id,
            'title': 'Review: ' + self.verbose_task_name,
            'change_link': 'nanny_your_children_summary',
            # The "Which of your children live with you?" lives under a separate table - the "Your children's
            # addresses table". The general_table_template does not currently support multiple tables per task.
            'children_living_with_applicant': children_living_with_you_response_string,
            'children_living_with_you_form': children_living_with_you_form,

            # Summary page will attempt to render a single table to then be populated with rows.
            # This needs to be overridden and the custom 'your-children' templates used.
            'skip_summary_page_title': True,

            'rows': [
                {
                    'id': 'your_children_details',
                    'info': children_records,
                    'formset': children_formset
                }
            ]
        }

        return context
