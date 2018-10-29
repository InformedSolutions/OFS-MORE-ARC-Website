from arc_application.forms.nanny_forms.nanny_form_builder import ChildcareAddressFormset, WhereYouWillWorkForm
from arc_application.services.arc_comments_handler import get_form_initial_values
from arc_application.services.db_gateways import NannyGatewayActions

from .nanny_form_view import NannyARCFormView


class NannyChildcareAddressSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_first_aid_training_summary'
    task_for_review = 'childcare_address_review'
    verbose_task_name = 'Childcare address'
    form_class = [WhereYouWillWorkForm, ChildcareAddressFormset]

    def get_context_data(self, application_id):
        nanny_actions = NannyGatewayActions()
        nanny_application = nanny_actions.read('application',
                                               params={'application_id': application_id}).record
        home_address_info = nanny_actions.read('applicant-home-address',
                                               params={'application_id': application_id,
                                                       'current_address': True}).record
        childcare_address_info = nanny_actions.read('applicant-home-address',
                                               params={'application_id': application_id,
                                                       'childcare_address': True}).record

        work_location_bool = nanny_application['address_to_be_provided']
        if home_address_info == childcare_address_info:
            work_at_home_bool = 'Yes'
        else:
            work_at_home_bool = 'No'

        if work_location_bool:
            home_address_locations = nanny_actions.list('childcare-address',
                                                        params={'application_id': application_id}).record
        else:
            home_address_locations = {}

        where_you_will_work_form = WhereYouWillWorkForm()  # TODO: call get initial on this

        n_forms = str(len(home_address_locations))

        childcare_address_formset = ChildcareAddressFormset(
            data={
                'form-TOTAL_FORMS': n_forms,
                'form-INITIAL_FORMS': n_forms,
                'form-MAX_NUM_FORMS': n_forms,
            }
        )

        initial_vals = get_form_initial_values(childcare_address_formset, application_id)

        childcare_address_formset = ChildcareAddressFormset(initial=initial_vals)

        context = {
            'application_id': application_id,
            'title': 'Review: Childcare address',
            'rows': [
                {
                    'id': 'address_to_be_provided',
                    'name': "Do you know where you'll be working?",
                    'info': work_location_bool,
                    'declare': where_you_will_work_form['address_to_be_provided_declare'],
                    'comments': where_you_will_work_form['address_to_be_provided_comments']
                },
                {
                    'id': 'work_at_home_bool',
                    'name': 'Will you work and live at the same address?',
                    'info': work_at_home_bool
                },
                {
                    'id': 'home_address_locations',
                    'name': 'Childcare address',
                    'info': home_address_locations,
                    'formset': childcare_address_formset
                },
            ]
        }

        return context
