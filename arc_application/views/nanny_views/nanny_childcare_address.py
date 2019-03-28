from .nanny_form_view import NannyARCFormView
from ...forms.nanny_forms.form_data import WHERE_YOU_WILL_WORK_DATA, CHILDCARE_ADDRESS_DATA
from ...forms.nanny_forms.nanny_forms import ChildcareAddressFormset, WhereYouWillWorkForm
from ...services.db_gateways import NannyGatewayActions


class NannyChildcareAddressSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_first_aid_training_summary'
    task_for_review = 'childcare_address_review'
    verbose_task_name = 'Childcare address'
    form_class = [WhereYouWillWorkForm, ChildcareAddressFormset]

    def get_context_data(self, application_id):
        self.application_id = application_id

        nanny_actions = NannyGatewayActions()
        nanny_application = nanny_actions.read('application',
                                               params={'application_id': application_id}).record

        work_location_bool = nanny_application['address_to_be_provided']

        where_you_will_work_form = self.get_form(form_class=self.form_class[0])

        # If applicant has opted to provide addresses at a later time, skip remainder of summary page - load only this.
        if not work_location_bool:
            context = {
                'application_id': application_id,
                'title': 'Review: Childcare address',
                'rows': [
                    {
                        'id': 'address_to_be_provided',
                        'name': WHERE_YOU_WILL_WORK_DATA['address_to_be_provided'],
                        'info': work_location_bool,
                        'declare': where_you_will_work_form['address_to_be_provided_declare'] if hasattr(self,
                                                                                                         'request') else '',
                        'comments': where_you_will_work_form['address_to_be_provided_comments']
                    },
                ]
            }

            return context

        home_address_info = nanny_actions.read('applicant-home-address',
                                               params={'application_id': application_id,
                                                       'current_address': True}).record
        childcare_address_info = nanny_actions.read('applicant-home-address',
                                                    params={'application_id': application_id,
                                                            'childcare_address': True}).record

        if home_address_info == childcare_address_info:
            work_at_home_bool = 'Yes'
        else:
            work_at_home_bool = 'No'

        if work_location_bool:
            home_address_locations = nanny_actions.list('childcare-address',
                                                        params={'application_id': application_id}).record
        else:
            home_address_locations = {}

        where_you_will_work_form, childcare_address_formset = self.get_forms()

        context = {
            'application_id': application_id,
            'title': 'Review: Childcare address',
            'change_link': 'nanny_childcare_address_summary',
            'rows': [
                {
                    'id': 'address_to_be_provided',
                    'name': WHERE_YOU_WILL_WORK_DATA['address_to_be_provided'],
                    'info': work_location_bool,
                    'declare': where_you_will_work_form['address_to_be_provided_declare'] if hasattr(self,
                                                                                                     'request') else '',
                    'comments': where_you_will_work_form['address_to_be_provided_comments']
                },
                {
                    'id': 'both_work_and_home_address',
                    'name': WHERE_YOU_WILL_WORK_DATA['both_work_and_home_address'],
                    'info': work_at_home_bool,
                    'declare': where_you_will_work_form['both_work_and_home_address_declare'] if hasattr(self,
                                                                                                         'request') else '',
                    'comments': where_you_will_work_form['both_work_and_home_address_comments']
                },
                {
                    'id': 'home_address_locations',
                    'name': CHILDCARE_ADDRESS_DATA['childcare_address'],
                    'info': home_address_locations,
                    'formset': childcare_address_formset
                }
            ]
        }

        return context
