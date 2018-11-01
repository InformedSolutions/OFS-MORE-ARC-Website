from .nanny_form_view import NannyARCFormView
from ...forms.nanny_forms.nanny_form_builder import FirstAidForm
from ...services.db_gateways import NannyGatewayActions


class NannyYourChildrenSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_childcare_address_summary'
    task_for_review = 'your_children_review'
    verbose_task_name = 'Your children'
    form_class = FirstAidForm

    def get_context_data(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        self.application_id = application_id
        nanny_actions = NannyGatewayActions()
        # TODO Get dict when nanny_gateway has your-children endpoint
        # your_children_dict = nanny_actions.read('your-children',
        #                                         params={'application_id': application_id}).record

        form = self.get_form()

        context = {
            'application_id': application_id,
            'title': 'Review: ' + self.verbose_task_name,
            'form': form,
            'rows': [
                # TODO Add rows when your children task is complete
                # {
                #     'id': 'training_organisation',
                #     'name': 'Training organisation',
                #     'info': training_organisation,
                #     # Prevent checkbox appearing if summary page is calling get_context_data.
                #     'declare': form['training_organisation_declare'] if hasattr(self, 'request') else '',
                #     'comments': form['training_organisation_comments']
                # }
            ]
        }

        return context
