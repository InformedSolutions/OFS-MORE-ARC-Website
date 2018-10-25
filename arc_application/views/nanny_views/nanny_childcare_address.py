from arc_application.forms.nanny_forms.nanny_form_builder import ChildcareAddressForm, WhereYouWillWorkForm
from arc_application.services.db_gateways import NannyGatewayActions

from .nanny_form_view import NannyARCFormView


class NannyChildcareAddressSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_first_aid_training_summary'
    task_for_review = 'childcare_address_review'
    verbose_task_name = 'Childcare address'
    form_class = [WhereYouWillWorkForm,]

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

        where_you_will_work_form = WhereYouWillWorkForm()

        from django.forms import formset_factory

        ChildcareAddressFormset = formset_factory(ChildcareAddressForm, extra=0)
        childcare_address_formset = ChildcareAddressFormset(
            data={
                'form-TOTAL_FORMS': str(len(home_address_locations)),
                'form-INITIAL_FORMS': str(len(home_address_locations)),
                'form-MAX_NUM_FORMS': str(len(home_address_locations)),
            }
        )

        for index, form in enumerate(childcare_address_formset):
            form.fields['childcare_address_declare'].widget.attrs.update(
                {
                    'data_target': 'childcare_address_' + str(index + 1),
                    'aria-controls': 'childcare_address_' + str(index + 1),
                    'aria-expanded': 'false'
                }
            )

        print('Break')

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
