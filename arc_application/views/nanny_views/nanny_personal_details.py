import datetime
from urllib.parse import urlencode

from .nanny_form_view import NannyARCFormView
from ...forms.nanny_forms.nanny_form_builder import HomeAddressForm, PersonalDetailsForm, PreviousRegistrationForm
from ...services.db_gateways import NannyGatewayActions
from ...utils import spatial_ordinal


class NannyPersonalDetailsSummary(NannyARCFormView):

    template_name = 'nanny_personal_details_summary.html'
    task_for_review = 'personal_details_review'
    verbose_task_name = 'Your personal details'

    def get_form_class(self, **kwargs):
        if hasattr(self, 'request'):
            application_id = self.request.GET.get('id')
        else:
            application_id = kwargs.pop('application_id')

        previous_registration_details = self.read_record(NannyGatewayActions(), 'previous-registration-details',
                                                         {'application_id': application_id})
        forms = [PersonalDetailsForm, HomeAddressForm]
        if previous_registration_details is not None:
            forms.append(PreviousRegistrationForm)

        return forms

    @staticmethod
    def format_date(iso_date_str):
        """
        :param iso_date_str: a Date Of Birth string in the format 'YYYY-MM-DD'
        :return: a DOB string in format 'DD-Month-YYYY'
        """
        the_date = datetime.datetime.strptime(iso_date_str, '%Y-%M-%d').date()
        return the_date.strftime('%d/%m/%Y')

    @staticmethod
    def format_name(first, middles, last):
        return first + ((' ' + middles) if middles else '') + ' ' + last

    def list_records(self, actions, endpoint, params):
        return self._do_get_records(actions, 'list', endpoint, params)

    def read_record(self, actions, endpoint, params):
        return self._do_get_records(actions, 'read', endpoint, params)

    @staticmethod
    def _do_get_records(actions, which_action, endpoint, params):
        response = getattr(actions, which_action)(endpoint, params=params)
        if response.status_code != 200 or not hasattr(response, 'record'):
            return None
        return response.record

    def get_context_data(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        self.application_id = application_id
        nanny_actions = NannyGatewayActions()
        personal_details = self.read_record(nanny_actions, 'applicant-personal-details',
                                            {'application_id': application_id})
        home_address = self.read_record(nanny_actions, 'applicant-home-address',
                                        {'application_id': application_id})
        previous_addresses = self.list_records(nanny_actions, 'previous-address',
                                               {'person_id': application_id, 'person_type': 'APPLICANT'})
        previous_registration_details = self.read_record(nanny_actions, 'previous-registration-details',
                                                         {'application_id': application_id})

        first_name = personal_details['first_name']
        middle_names = personal_details['middle_names']
        last_name = personal_details['last_name']
        full_name = self.format_name(first_name, middle_names, last_name)

        dob_string = personal_details['date_of_birth']
        dob_string_with_month = self.format_date(dob_string)

        street_line1 = home_address['street_line1']
        street_line2 = home_address['street_line2']
        town = home_address['town']
        county = home_address['county']
        postcode = home_address['postcode']

        known_to_social_services = personal_details['known_to_social_services']
        reasons_known_to_social_services = personal_details['reasons_known_to_social_services']

        previous_registration_record_exists = False
        show_individual_id = False

        forms = self.get_forms(application_id)
        personal_details_form = forms[0]
        home_address_form = forms[1]

        if previous_registration_details is not None:
            previous_registration_record_exists = True
            previous_registration_details = nanny_actions.read('previous-registration-details',
                                                               params={'application_id': application_id}).record
            previous_registration = previous_registration_details['previous_registration']
            individual_id = str(previous_registration_details['individual_id'])
            five_years_in_UK = previous_registration_details['five_years_in_UK']
            previous_registration_form = forms[2]

            if previous_registration is True:
                show_individual_id = True

        rows = [
            {
                'id': 'name',
                'name': 'Your name',
                'info': full_name,
                # Prevent checkbox appearing if summary page is calling get_context_data.
                'declare': personal_details_form['name_declare'] if hasattr(self, 'request') else '',
                'comments': personal_details_form['name_comments'],
            },
            {
                'id': 'date_of_birth',
                'name': 'Date of birth',
                'info': dob_string_with_month,
                'declare': personal_details_form['date_of_birth_declare'] if hasattr(self, 'request') else '',
                'comments': personal_details_form['date_of_birth_comments'],
            },
            {
                'id': 'home_address',
                'name': 'Your home address',
                'declare': home_address_form['home_address_declare'] if hasattr(self, 'request') else '',
                'comments': home_address_form['home_address_comments'],
                'info': {
                    'street_line1': street_line1,
                    'street_line2': street_line2,
                    'town': town,
                    'county': county,
                    'postcode': postcode,
                }
            },
        ]
        for i, prev_addr in enumerate(previous_addresses or []):
            addr_change_view = 'nanny_previous_addresses'
            addr_change_params = urlencode({'person_id': application_id, 'type': 'APPLICANT'})
            rows.extend([
                {
                    'id': 'previous_home_address'.format(i+1),
                    'name': 'Previous home address {}'.format(i+1),
                    'info': {
                        'street_line1': prev_addr['street_line1'],
                        'street_line2': prev_addr['street_line2'],
                        'town': prev_addr['town'],
                        'county': prev_addr['county'],
                        'postcode': prev_addr['postcode'],
                    },
                    'change_link': addr_change_view,
                    'change_link_params': addr_change_params,
                    'change_link_alt': 'Change the {} previous address'
                                       .format(spatial_ordinal(i+1)),
                },
                {
                    'id': 'previous_home_address',
                    'name': 'Moved in',
                    'info': self.format_date(prev_addr['moved_in_date']),
                    'change_link': addr_change_view,
                    'change_link_params': addr_change_params,
                    'change_link_alt': 'Change the move in date for the {} previous address'
                                       .format(spatial_ordinal(i+1)),
                },
                {
                    'id': 'previous_home_address',
                    'name': 'Moved out',
                    'info': self.format_date(prev_addr['moved_out_date']),
                    'change_link': addr_change_view,
                    'change_link_params': addr_change_params,
                    'change_link_alt': 'Change the move out date for the {} previous address'
                                       .format(spatial_ordinal(i+1)),
                },
            ])
        rows.append(
            {
                'id': 'known_to_social_services',
                'name': 'Known to council social Services?',
                'info': known_to_social_services,
                'declare': personal_details_form['known_to_social_services_declare']
                           if hasattr(self, 'request') else '',
                'comments': personal_details_form['known_to_social_services_comments'],
            }
        )
        if known_to_social_services is True:
            rows.append(
                {
                    'id': 'reasons_known_to_social_services',
                    'name': 'Tell us why',
                    'info': reasons_known_to_social_services,
                    'declare': personal_details_form['reasons_known_to_social_services_declare']
                               if hasattr(self, 'request') else '',
                    'comments': personal_details_form['reasons_known_to_social_services_comments'],
                }
            )

        if previous_registration_record_exists is True:
            rows.append(
                {
                    'id': 'previous_registration',
                    'name': 'Previously registered with Ofsted?',
                    'info': previous_registration,
                    'declare': previous_registration_form['previous_registration_declare']
                               if hasattr(self, 'request') else '',
                    'comments': previous_registration_form['previous_registration_comments'],
                })
            # required for conditional reveal of individual_id on master summary
            if previous_registration is True:
                rows.append(
                    {
                        'id': 'individual_id',
                        'name': 'Individual ID',
                        'info': individual_id,
                        'declare': previous_registration_form['individual_id_declare']
                                   if hasattr(self, 'request') else '',
                        'comments': previous_registration_form['individual_id_comments'],
                    })
            rows.append(
                {
                    'id': 'five_years_in_UK',
                    'name': 'Lived in England for more than 5 years?',
                    'info': five_years_in_UK,
                    'declare': previous_registration_form['five_years_in_UK_declare']
                               if hasattr(self, 'request') else '',
                    'comments': previous_registration_form['five_years_in_UK_comments'],
                })

        context = {
            'application_id': application_id,
            'title': 'Review: ' + self.verbose_task_name,
            'show_previous_registration':  previous_registration_record_exists,
            # used for conditional reveal of individual_id on summary page
            'show_individual_id': show_individual_id,
            'change_link': 'nanny_personal_details_summary',
            'rows': rows,
        }

        return context

    def get_forms(self, application_id):
        return [self.get_form(form_class=form_class)
                for form_class in self.get_form_class(application_id=application_id)]

    def get_success_url(self):
        return 'nanny_childcare_address_summary'
