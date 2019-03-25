import datetime
from urllib.parse import urlencode

from .nanny_form_view import NannyARCFormView
from ...forms.nanny_forms.nanny_form_builder import HomeAddressForm, PersonalDetailsForm, PreviousRegistrationForm
from ...services.db_gateways import NannyGatewayActions
from operator import itemgetter
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
    def format_date(date_or_iso_str):
        """
        :param date_or_iso_str: a date object or string in the format 'YYYY-MM-DD'
        :return: a date string in the format 'DD/MM/YYYY'
        """
        if isinstance(date_or_iso_str, datetime.date):
            the_date = date_or_iso_str
        else:
            the_date = datetime.datetime.strptime(date_or_iso_str, '%Y-%m-%d').date()
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
        previous_names = self.list_records(nanny_actions, 'previous-name', 
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
        current_full_name = self.format_name(first_name, middle_names, last_name)

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
                'info': current_full_name,
                # Prevent checkbox appearing if summary page is calling get_context_data.
                'declare': personal_details_form['name_declare'] if hasattr(self, 'request') else '',
                'comments': personal_details_form['name_comments'],
            }
        ]

        if previous_names is not None and len(previous_names) > 0:
            for i, name in enumerate(previous_names):
                full_name = self.format_name(name['first_name'], name['middle_names'], name['last_name'])
                start_date = datetime.date(name['start_year'], name['start_month'], name['start_day'])
                end_date = datetime.date(name['end_year'], name['end_month'], name['end_day'])
                ordinal = spatial_ordinal(i+1)
                rows.extend([
                    {
                        'id': 'previous_name',
                        'name': 'Previous name {}'.format(i+1),
                        'info': full_name,
                        'change_link': 'nanny_previous_names',
                        'alt_text': "Change the {0} previous name".format(ordinal)
                    },
                    {
                        'id': 'start_date',
                        'name': 'Start date',
                        'info': self.format_date(start_date),
                        'change_link': 'nanny_previous_names',
                        'alt_text': "Change the start date for the {0} previous name".format(ordinal)
                    },
                    {
                        'id': 'end_date',
                        'name': 'End date',
                        'info': self.format_date(end_date),
                        'change_link': 'nanny_previous_names',
                        'alt_text':"Change the end date for the {0} previous name".format(ordinal)
                    },
                ])

        rows.extend([
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
        ])
        for i, prev_addr in enumerate(previous_addresses or []):
            addr_change_view = 'nanny_change_previous_address'
            addr_change_params = urlencode({'previous_address_id': prev_addr['previous_address_id']})
            rows.extend([
                {
                    'id': 'previous_home_address',
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
        self.__handle_previous_name_and_address_dates()
        return 'nanny_childcare_address_summary'

    def __handle_previous_name_and_address_dates(self):
        """
        Sets start and end dates for current name and address in db
        """
        actions = NannyGatewayActions()
        end_date = datetime.date.today()
        personal_details = self.read_record(actions, 'applicant-personal-details',
                                            {'application_id': self.application_id})
        date_of_birth = datetime.datetime.strptime(personal_details['date_of_birth'], '%Y-%m-%d').date()

        previous_names = self.list_records(actions, 'previous-name', {'application_id': self.application_id})
        if previous_names is not None and len(previous_names) > 0:
            for name in previous_names:
                name['end_date'] = datetime.date(name['end_year'], name['end_month'], name['end_day'])
            sorted_previous_names = sorted(previous_names, key=itemgetter('end_date'), reverse=True)
            name_start_date = sorted_previous_names[0]['end_date']
        else:
            name_start_date = date_of_birth

        personal_details['name_start_day'] = name_start_date.day
        personal_details['name_start_month'] = name_start_date.month
        personal_details['name_start_year'] = name_start_date.year
        personal_details['name_end_day'] = end_date.day
        personal_details['name_end_month'] = end_date.month
        personal_details['name_end_year'] = end_date.year

        previous_addresses = self.list_records(actions, 'previous-address',
                                               {'person_id': self.application_id, 'person_type': 'APPLICANT'})
        if previous_addresses is not None and len(previous_addresses) > 0:
            # moved_out_date is a string but due to iso format, lexicographical order will be
            # equivalent to chronological
            sorted_previous_addresses = sorted(previous_addresses, key=itemgetter('moved_out_date'), reverse=True)
            address_start_date = datetime.datetime.strptime(sorted_previous_addresses[0]['moved_out_date'],
                                                            '%Y-%m-%d').date()
        else:
            address_start_date = date_of_birth

        personal_details['moved_in_date'] = address_start_date
        personal_details['moved_out_date'] = end_date

        actions.put('applicant-personal-details', params=personal_details)
