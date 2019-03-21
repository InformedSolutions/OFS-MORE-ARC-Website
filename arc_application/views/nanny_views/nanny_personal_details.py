import datetime

from .nanny_form_view import NannyARCFormView
from ...forms.nanny_forms.nanny_form_builder import HomeAddressForm, PersonalDetailsForm, PreviousRegistrationForm
from ...services.db_gateways import NannyGatewayActions
import inflect
from operator import itemgetter


class NannyPersonalDetailsSummary(NannyARCFormView):
    template_name = 'nanny_personal_details_summary.html'
    task_for_review = 'personal_details_review'
    verbose_task_name = 'Your personal details'

    def get_form_class(self, **kwargs):
        if hasattr(self, 'request'):
            application_id = self.request.GET.get('id')
        else:
            application_id = kwargs.pop('application_id')

        previous_registration_details = NannyGatewayActions().read('previous-registration-details',
                                                                   params={'application_id': application_id})
        if previous_registration_details.status_code != 404:
            return [PersonalDetailsForm, HomeAddressForm, PreviousRegistrationForm]
        else:
            return [PersonalDetailsForm, HomeAddressForm]

    @staticmethod
    def month_converter(dob_string):
        """
        Converts a numerical month into the related string month.
        :param dob_string: a Date Of Birth string in the format 'YYYY-MM-DD'
        :return: a DOB string in format 'DD-Month-YYYY'
        """
        birth_datetime = datetime.datetime.strptime(dob_string, '%Y-%m-%d')

        return birth_datetime.strftime('%d/%m/%Y')

    def get_context_data(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        self.application_id = application_id
        nanny_actions = NannyGatewayActions()
        personal_details = nanny_actions.read('applicant-personal-details',
                                              params={'application_id': application_id}).record
        home_address = nanny_actions.read('applicant-home-address',
                                          params={'application_id': application_id}).record
        previous_registration_details = nanny_actions.read('previous-registration-details',
                                          params={'application_id': application_id})



        first_name = personal_details['first_name']
        middle_names = personal_details['middle_names']
        last_name = personal_details['last_name']
        full_name = "{0} {1} {2}".format(first_name, middle_names, last_name)

        dob_string = personal_details['date_of_birth']
        dob_string_with_month = self.month_converter(dob_string)

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

        if previous_registration_details.status_code != 404:
            previous_registration_record_exists = True
            previous_registration_details = nanny_actions.read('previous-registration-details',
                                                               params={'application_id': application_id}).record
            previous_registration = previous_registration_details['previous_registration']
            individual_id = str(previous_registration_details['individual_id'])
            five_years_in_UK = previous_registration_details['five_years_in_UK']
            previous_registration_form = forms[2]

            if previous_registration is True:
                show_individual_id = True

        previous_names_response = nanny_actions.list('previous-name',
                                                               params={'application_id': application_id})

        previous_names = []
        inflect_engine = inflect.engine()
        if previous_names_response.status_code == 200:
            previous_names_list = previous_names_response.record
            for name in previous_names_list:
                first_name = name['first_name']
                middle_names = name['middle_names']
                last_name = name['last_name']
                full_name = "{0} {1} {2}".format(first_name, middle_names, last_name)
                start_date_datetime = datetime.date(name['start_year'], name['start_month'], name['start_day'])
                start_date = start_date_datetime.strftime('%d/%m/%Y')
                end_date_datetime = datetime.date(name['end_year'], name['end_month'], name['end_day'])
                end_date = end_date_datetime.strftime('%d/%m/%Y')
                order = str(name['order'] + 1)
                ordinal = inflect_engine.ordinal(inflect_engine.number_to_words(order))
                previous_names.append(
                    {
                        'id': 'previous_name',
                        'name': 'Previous name '+ order,
                        'info': full_name,
                        'change_link': 'nanny_previous_names',
                        'alt_text': "Change the {0} previous name".format(ordinal)
                    })
                previous_names.append(
                    {
                        'id': 'start_date',
                        'name': 'Start date',
                        'info':start_date,
                        'change_link': 'nanny_previous_names',
                        'alt_text': "Change the start date for the {0} previous name".format(ordinal)
                    })
                previous_names.append(
                    {
                     'id': 'end_date',
                     'name': 'End date',
                     'info': end_date,
                    'change_link': 'nanny_previous_names',
                        'alt_text':"Change the end date for the {0} previous name".format(ordinal)
                     })


        context = {
            'application_id': application_id,
            'title': 'Review: ' + self.verbose_task_name,
            'show_previous_registration':  previous_registration_record_exists,
            #used for conditional reveal of individual_id on summary page
            'show_individual_id' : show_individual_id,
            'change_link': 'nanny_personal_details_summary',
            'rows': [
                {
                    'id': 'name',
                    'name': 'Your name',
                    'info': full_name,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'declare': personal_details_form['name_declare'] if hasattr(self, 'request') else '',
                    'comments': personal_details_form['name_comments'],
                }]}

        if any(previous_names):
            context['rows'] += previous_names


        context['rows'].append({
                    'id': 'date_of_birth',
                    'name': 'Date of birth',
                    'info': dob_string_with_month,
                    'declare': personal_details_form['date_of_birth_declare'] if hasattr(self, 'request') else '',
                    'comments': personal_details_form['date_of_birth_comments'],
                })

        context['rows'].append ({
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
                })

        context['rows'].append(
                {
                    'id': 'known_to_social_services',
                    'name': 'Known to council social Services?',
                    'info': known_to_social_services,
                    'declare': personal_details_form['known_to_social_services_declare'] if hasattr(self,
                                                                                                    'request') else '',
                    'comments': personal_details_form['known_to_social_services_comments'],

                })


        if known_to_social_services is True:
            context['rows'].append(
                {
                    'id': 'reasons_known_to_social_services',
                    'name': 'Tell us why',
                    'info': reasons_known_to_social_services,
                    'declare': personal_details_form['reasons_known_to_social_services_declare'] if hasattr(self,
                                                                                                            'request') else '',
                    'comments': personal_details_form['reasons_known_to_social_services_comments'],
                }
            )

        if previous_registration_record_exists is True:
            context['rows'].append(
                {
                    'id': 'previous_registration',
                    'name': 'Previously registered with Ofsted?',
                    'info': previous_registration,
                    'declare': previous_registration_form['previous_registration_declare'] if hasattr(self,
                                                                                                      'request') else '',
                    'comments': previous_registration_form['previous_registration_comments'],
                })
            #required for conditional reveal of individual_id on master summary
            if previous_registration is True:
                context['rows'].append(
                    {
                        'id': 'individual_id',
                        'name': 'Individual ID',
                        'info': individual_id,
                        'declare': previous_registration_form['individual_id_declare'] if hasattr(self, 'request') else '',
                        'comments': previous_registration_form['individual_id_comments'],
                    })
            context['rows'].append(
                {
                    'id': 'five_years_in_UK',
                    'name': 'Lived in England for more than 5 years?',
                    'info': five_years_in_UK,
                    'declare': previous_registration_form['five_years_in_UK_declare'] if hasattr(self,
                                                                                                 'request') else '',
                    'comments': previous_registration_form['five_years_in_UK_comments'],
                })

        return context

    def get_forms(self, application_id):
        return [self.get_form(form_class=form_class) for form_class in self.get_form_class(application_id=application_id)]

    def get_success_url(self):
        self.__handle_previous_name_dates()
        return 'nanny_childcare_address_summary'

    def __handle_previous_name_dates(self):
        """
        Function to get start_date for current name and update start and end date for current name in db
        """
        previous_names_response = NannyGatewayActions().list('previous-name', params={'application_id': self.application_id})
        personal_details_response = NannyGatewayActions().read('applicant-personal-details',
                                                               params={'application_id': self.application_id})
        end_date = datetime.date.today()
        if personal_details_response.status_code == 200:
            pd_record = personal_details_response.record
            if previous_names_response.status_code == 200:
                previous_names_list = previous_names_response.record
                for name in previous_names_list:
                    name['end_date'] = datetime.date(name['end_year'], name['end_month'], name['end_day'])
                sorted_previous_names = sorted(previous_names_list, key=itemgetter('end_date'), reverse=True)
                start_date = sorted_previous_names[0]['end_date']

            else:
                start_date = datetime.datetime.strptime(pd_record['date_of_birth'], "%Y-%m-%d")

            pd_record['name_start_day'] = start_date.day
            pd_record['name_start_month'] = start_date.month
            pd_record['name_start_year'] = start_date.year
            pd_record['name_end_day'] = end_date.day
            pd_record['name_end_month'] = end_date.month
            pd_record['name_end_year'] = end_date.year
            NannyGatewayActions().put('applicant-personal-details', params=pd_record)
